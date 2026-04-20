"""CLI to run an eval config end-to-end."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pathlib import Path

import typer
import yaml
from pydantic import BaseModel
from sqlalchemy.orm import Session

from rigor.core.runner import execute_run
from rigor.datasets.loaders import load_humaneval
from rigor.db.models import Model, Prompt, Run
from rigor.db.session import SessionLocal, create_all

app = typer.Typer()

DEFAULT_CODEGEN_TEMPLATE = (
    "Complete the following Python function. "
    "Output only the function body, no explanation.\n\n{{ prompt }}"
)


class PromptConfig(BaseModel):
    name: str
    version: int
    template: str = DEFAULT_CODEGEN_TEMPLATE


class ModelConfig(BaseModel):
    name: str
    provider: str


class EvalConfig(BaseModel):
    dataset: str
    prompt: PromptConfig
    models: list[ModelConfig]
    sample_params: dict = {}
    metrics: list[str] = []


def _get_or_create_model(session: Session, name: str, provider: str) -> Model:
    model = session.query(Model).filter_by(name=name, provider=provider).first()
    if not model:
        model = Model(name=name, provider=provider)
        session.add(model)
        session.commit()
    return model


def _get_or_create_prompt(session: Session, cfg: PromptConfig) -> Prompt:
    prompt = session.query(Prompt).filter_by(name=cfg.name, version=cfg.version).first()
    if not prompt:
        prompt = Prompt(name=cfg.name, version=cfg.version, template=cfg.template)
        session.add(prompt)
        session.commit()
    return prompt


@app.command()
def main(config_path: Path = typer.Argument(..., help="Path to eval YAML config")) -> None:
    raw = yaml.safe_load(config_path.read_text())
    cfg = EvalConfig(**raw)

    create_all()

    session: Session = SessionLocal()
    try:
        if cfg.dataset == "humaneval-50":
            typer.echo("Loading humaneval-50 dataset...")
            dataset = load_humaneval(session)
            typer.echo(f"  Dataset ready: {dataset.example_count} examples")
        else:
            raise typer.BadParameter(f"Unknown dataset: {cfg.dataset}")

        prompt = _get_or_create_prompt(session, cfg.prompt)

        for model_cfg in cfg.models:
            typer.echo(f"\nRunning model: {model_cfg.name} ({model_cfg.provider})")
            model = _get_or_create_model(session, model_cfg.name, model_cfg.provider)

            run_config = cfg.model_dump()
            run = Run(
                dataset_id=dataset.id,
                model_id=model.id,
                prompt_id=prompt.id,
                config=run_config,
                status="pending",
            )
            session.add(run)
            session.commit()

            execute_run(run.id, session)

            session.refresh(run)
            n_results = len(run.results)
            n_errors = sum(1 for r in run.results if r.error)
            typer.echo(
                f"  run_id={run.id}  status={run.status}  "
                f"results={n_results}  errors={n_errors}"
            )

    finally:
        session.close()


if __name__ == "__main__":
    app()
