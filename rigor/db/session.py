"""SQLAlchemy sync session factory and create_all() helper."""

# TODO: Configure SQLAlchemy 2.0 sync engine from DATABASE_URL setting.
#   Expose a SessionLocal sessionmaker and a create_all() function that calls
#   Base.metadata.create_all() — called on app startup (no Alembic for week 1).
