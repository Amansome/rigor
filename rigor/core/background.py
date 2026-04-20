"""Background task helpers for running evals outside the request session."""

import logging
from uuid import UUID

logger = logging.getLogger(__name__)


def execute_run_in_new_session(run_id: UUID) -> None:
    from rigor.core.runner import execute_run
    from rigor.db.session import SessionLocal

    session = SessionLocal()
    try:
        execute_run(run_id, session)
    except Exception:
        logger.exception("Background run execution raised unexpectedly")
    finally:
        session.close()
