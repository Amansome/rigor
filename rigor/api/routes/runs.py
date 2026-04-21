"""Routes for /api/v1/runs."""

import math
import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from rigor.api.schemas import (
    BootstrapCIResponse,
    CreateRunRequest,
    ResultResponse,
    RunResponse,
    RunSummaryResponse,
)
from rigor.core.background import execute_run_in_new_session
from rigor.db.models import Dataset, Model, Prompt, Result, Run
from rigor.db.session import get_db
from rigor.stats.bootstrap import bootstrap_ci

router = APIRouter()


@router.get("/runs", response_model=list[RunResponse])
def list_runs(
    dataset_name: str | None = None,
    model_name: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
) -> list[Run]:
    q = db.query(Run)
    if dataset_name:
        q = q.join(Run.dataset).filter(Dataset.name == dataset_name)
    if model_name:
        q = q.join(Run.model).filter(Model.name == model_name)
    if status:
        q = q.filter(Run.status == status)
    return q.order_by(Run.created_at.desc()).limit(100).all()


@router.get("/runs/{run_id}", response_model=RunResponse)
def get_run(run_id: uuid.UUID, db: Session = Depends(get_db)) -> Run:
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/runs/{run_id}/results", response_model=list[ResultResponse])
def get_run_results(
    run_id: uuid.UUID,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: Session = Depends(get_db),
) -> list[Result]:
    if db.get(Run, run_id) is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return (
        db.query(Result)
        .filter_by(run_id=run_id)
        .order_by(Result.created_at)
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/runs/{run_id}/summary", response_model=RunSummaryResponse)
def get_run_summary(run_id: uuid.UUID, db: Session = Depends(get_db)) -> RunSummaryResponse:
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    results = db.query(Result).filter_by(run_id=run_id).all()
    n_results = len(results)
    n_errors = sum(1 for r in results if r.error is not None)

    # Collect per-example scores for each metric key across all results.
    scores_by_metric: dict[str, list[float]] = {}
    for r in results:
        for k, v in (r.metrics or {}).items():
            if v is None or (isinstance(v, float) and math.isnan(v)):
                # Skip NaN/None values defensively — shouldn't happen with current metrics
                continue
            scores_by_metric.setdefault(k, []).append(float(v))

    metrics: dict[str, BootstrapCIResponse] = {}
    for metric_name, scores in scores_by_metric.items():
        ci = bootstrap_ci(scores)
        metrics[metric_name] = BootstrapCIResponse(
            mean=ci.mean,
            ci_low=ci.ci_low,
            ci_high=ci.ci_high,
            n_samples=ci.n_samples,
            confidence=ci.confidence,
            n_iterations=ci.n_iterations,
        )

    return RunSummaryResponse(
        run_id=run_id,
        status=run.status,
        n_results=n_results,
        n_errors=n_errors,
        metrics=metrics,
    )


@router.post("/runs", response_model=RunResponse, status_code=202)
def create_run(
    body: CreateRunRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> Run:
    dataset = db.query(Dataset).filter_by(name=body.dataset_name).first()
    if dataset is None:
        raise HTTPException(status_code=404, detail=f"Dataset '{body.dataset_name}' not found")

    model = db.query(Model).filter_by(name=body.model_name, provider=body.provider).first()
    if model is None:
        raise HTTPException(
            status_code=404,
            detail=f"Model '{body.model_name}' (provider={body.provider}) not found",
        )

    prompt = db.query(Prompt).filter_by(name=body.prompt_name, version=body.prompt_version).first()
    if prompt is None:
        raise HTTPException(
            status_code=404,
            detail=f"Prompt '{body.prompt_name}' version {body.prompt_version} not found",
        )

    config = {
        "dataset_name": body.dataset_name,
        "model_name": body.model_name,
        "provider": body.provider,
        "prompt_name": body.prompt_name,
        "prompt_version": body.prompt_version,
        "sample_params": body.sample_params,
        "metrics": ["pass_at_1", "exact_match"],
    }

    run = Run(
        dataset_id=dataset.id,
        model_id=model.id,
        prompt_id=prompt.id,
        config=config,
        status="pending",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    background_tasks.add_task(execute_run_in_new_session, run.id)
    return run
