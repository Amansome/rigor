"""Routes for /api/v1/models."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from rigor.api.schemas import ModelResponse
from rigor.db.models import Model
from rigor.db.session import get_db

router = APIRouter()


@router.get("/models", response_model=list[ModelResponse])
def list_models(db: Session = Depends(get_db)) -> list[Model]:
    return db.query(Model).order_by(Model.created_at).all()
