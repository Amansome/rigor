"""Pure query helpers for the eval database."""

import uuid

from sqlalchemy.orm import Session

from rigor.db.models import Example, Result


def get_paired_scores(
    session: Session,
    run_a_id: uuid.UUID,
    run_b_id: uuid.UUID,
    metric: str,
) -> tuple[list[float], list[float]]:
    """Return aligned per-example scores for the given metric, in example.idx order.

    Only examples present in BOTH runs are returned. The two lists are the same
    length; pairs are aligned by example.
    """
    def _scores_for_run(run_id: uuid.UUID) -> dict[uuid.UUID, float]:
        rows = (
            session.query(Result.example_id, Result.metrics)
            .filter(Result.run_id == run_id)
            .join(Result.example)
            .order_by(Example.idx)
            .all()
        )
        out: dict[uuid.UUID, float] = {}
        for example_id, metrics in rows:
            val = metrics.get(metric)
            out[example_id] = float(val) if val is not None else float("nan")
        return out

    scores_a_map = _scores_for_run(run_a_id)
    scores_b_map = _scores_for_run(run_b_id)

    common_ids = sorted(
        scores_a_map.keys() & scores_b_map.keys(),
        key=lambda eid: session.query(Example.idx).filter(Example.id == eid).scalar(),
    )

    scores_a = [scores_a_map[eid] for eid in common_ids]
    scores_b = [scores_b_map[eid] for eid in common_ids]
    return scores_a, scores_b
