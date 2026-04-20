"""Routes for /api/v1/datasets."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from rigor.api.schemas import DatasetResponse
from rigor.db.models import Dataset
from rigor.db.session import get_db

router = APIRouter()


@router.get("/datasets", response_model=list[DatasetResponse])
def list_datasets(db: Session = Depends(get_db)) -> list[Dataset]:
    return db.query(Dataset).order_by(Dataset.created_at).all()


@router.get("/datasets/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: uuid.UUID, db: Session = Depends(get_db)) -> Dataset:
    dataset = db.get(Dataset, dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset
