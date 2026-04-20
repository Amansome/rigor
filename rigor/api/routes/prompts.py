"""Routes for /api/v1/prompts."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from rigor.api.schemas import CreatePromptRequest, PromptResponse
from rigor.db.models import Prompt
from rigor.db.session import get_db

router = APIRouter()


@router.get("/prompts", response_model=list[PromptResponse])
def list_prompts(db: Session = Depends(get_db)) -> list[Prompt]:
    return db.query(Prompt).order_by(Prompt.name, Prompt.version).all()


@router.post("/prompts", response_model=PromptResponse, status_code=201)
def create_prompt(body: CreatePromptRequest, db: Session = Depends(get_db)) -> Prompt:
    existing = db.query(Prompt).filter_by(name=body.name, version=body.version).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Prompt '{body.name}' version {body.version} already exists",
        )
    prompt = Prompt(name=body.name, version=body.version, template=body.template)
    db.add(prompt)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Prompt '{body.name}' version {body.version} already exists",
        )
    db.refresh(prompt)
    return prompt
