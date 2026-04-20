"""Eval runner: orchestrates a single Run end-to-end."""

import logging
from datetime import datetime, timezone
from uuid import UUID

from jinja2 import Template
from sqlalchemy.orm import Session

from rigor.db.models import Example, Result, Run
from rigor.metrics import registry
from rigor.models.litellm_adapter import generate

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def execute_run(run_id: UUID, session: Session) -> None:
    """Execute an eval run end-to-end. Updates run.status as it progresses."""
    run = session.get(Run, run_id)
    if run is None:
        raise ValueError(f"Run {run_id} not found")
    if run.status != "pending":
        raise ValueError(f"Run {run_id} has status '{run.status}', expected 'pending'")

    run.status = "running"
    run.started_at = _now()
    session.commit()

    try:
        dataset = run.dataset
        model = run.model
        prompt = run.prompt

        examples = (
            session.query(Example)
            .filter_by(dataset_id=dataset.id)
            .order_by(Example.idx)
            .all()
        )

        template = Template(prompt.template)

        provider = model.provider
        litellm_model = f"{provider}/{model.name}" if provider == "ollama" else model.name

        sample_params = run.config.get("sample_params", {})
        metric_names = run.config.get("metrics", [])

        for example in examples:
            output = ""
            latency_ms = 0
            input_tokens = None
            output_tokens = None
            cost_usd = None
            metrics: dict = {}
            error: str | None = None

            try:
                rendered_prompt = template.render(**example.input)
                gen = generate(litellm_model, rendered_prompt, sample_params or None)
                output = gen.output
                latency_ms = gen.latency_ms
                input_tokens = gen.input_tokens
                output_tokens = gen.output_tokens
                cost_usd = gen.cost_usd

                for name in metric_names:
                    try:
                        metric = registry.get(name)
                        metrics[name] = metric.compute(output, example.reference, example.input)
                    except KeyError:
                        logger.warning("Metric '%s' not registered, skipping", name)

            except Exception as exc:
                logger.error("Error on example %s: %s", example.idx, exc)
                error = str(exc)
                metrics = {}
                output = ""
                latency_ms = 0

            result = Result(
                run_id=run.id,
                example_id=example.id,
                output=output,
                latency_ms=latency_ms,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost_usd,
                metrics=metrics,
                error=error,
            )
            session.add(result)
            session.commit()

        run.status = "completed"
        run.completed_at = _now()
        session.commit()

    except Exception:
        run.status = "failed"
        session.commit()
        raise
