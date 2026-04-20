"""SQLAlchemy sync session factory and create_all() helper."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from rigor.core.config import get_settings

engine = create_engine(get_settings().database_url)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all() -> None:
    from rigor.db.models import Base  # noqa: PLC0415 — deferred to avoid circular import at module load
    Base.metadata.create_all(engine)
