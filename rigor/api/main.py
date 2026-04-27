"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rigor.api.routes import datasets, health, models, prompts, runs
from rigor.db.session import create_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all()
    yield


app = FastAPI(title="Rigor", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(models.router, prefix="/api/v1")
app.include_router(datasets.router, prefix="/api/v1")
app.include_router(prompts.router, prefix="/api/v1")
app.include_router(runs.router, prefix="/api/v1")
