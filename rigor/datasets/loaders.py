"""Dataset loaders: seed datasets into Postgres from source files."""

import gzip
import json

import httpx
from sqlalchemy.orm import Session

from rigor.db.models import Dataset, Example

HUMANEVAL_URL = (
    "https://raw.githubusercontent.com/openai/human-eval/master/data/HumanEval.jsonl.gz"
)


def load_humaneval(session: Session, limit: int = 50) -> Dataset:
    existing = session.query(Dataset).filter_by(name="humaneval-50").first()
    if existing:
        return existing

    response = httpx.get(HUMANEVAL_URL, follow_redirects=True, timeout=60.0)
    response.raise_for_status()

    raw = gzip.decompress(response.content)
    problems = [json.loads(line) for line in raw.decode().splitlines() if line.strip()]
    problems = problems[:limit]

    dataset = Dataset(
        name="humaneval-50",
        task_type="code_generation",
        example_count=len(problems),
    )
    session.add(dataset)
    session.flush()

    for idx, problem in enumerate(problems):
        example = Example(
            dataset_id=dataset.id,
            idx=idx,
            input={"prompt": problem["prompt"], "entry_point": problem["entry_point"]},
            reference={
                "canonical_solution": problem["canonical_solution"],
                "test": problem["test"],
            },
        )
        session.add(example)

    session.commit()
    return dataset
