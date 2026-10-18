from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import BeanRow, get_db
from app.schemas import Bean, BeanCreate, BeanUpdate, Roast

router = APIRouter(prefix="/api/catalog", tags=["catalog"])


@router.get("/beans", response_model=list[Bean])
def list_beans(roast: Roast | None = None, db: Session = Depends(get_db)):
    query = select(BeanRow).order_by(BeanRow.name)
    if roast is not None:
        query = query.where(BeanRow.roast == roast)
    return db.scalars(query).all()


@router.get("/beans/{bean_id}", response_model=Bean)
def get_bean(bean_id: int, db: Session = Depends(get_db)):
    bean = db.get(BeanRow, bean_id)
    if bean is None:
        raise HTTPException(status_code=404, detail="Bean not found")
    return bean


@router.post("/beans", response_model=Bean, status_code=201)
def create_bean(payload: BeanCreate, db: Session = Depends(get_db)):
    bean = BeanRow(**payload.model_dump())
    db.add(bean)
    db.commit()
    db.refresh(bean)
    return bean


@router.patch("/beans/{bean_id}", response_model=Bean)
def update_bean(bean_id: int, payload: BeanUpdate, db: Session = Depends(get_db)):
    bean = db.get(BeanRow, bean_id)
    if bean is None:
        raise HTTPException(status_code=404, detail="Bean not found")
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in changes.items():
        setattr(bean, field, value)
    db.commit()
    db.refresh(bean)
    return bean
