from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.poli import get_poli, get_polis, create_poli, update_poli, delete_poli
from app.schemas.poli import PoliCreate, PoliUpdate, PoliResponse

router = APIRouter(
    prefix="/poli",
    tags=["poli"]
)

@router.post("/", response_model=PoliResponse)
async def create(poli: PoliCreate, db: Session = Depends(get_db)):
    return await create_poli(db, poli)

@router.get("/", response_model=List[PoliResponse])
def get_all(db: Session = Depends(get_db)):
    return get_polis(db)

@router.get("/{poli_id}", response_model=PoliResponse)
def get_by_id(poli_id: int, db: Session = Depends(get_db)):
    poli = get_poli(db, poli_id)
    if not poli:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poli not found")
    
    return poli

@router.put("/{poli_id}", response_model=PoliResponse)
async def update(poli_id: int, poli: PoliUpdate, db: Session = Depends(get_db)):
    updated = await update_poli(db, poli_id, poli)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poli not found")
    
    return updated

@router.delete("/{poli_id}")
def delete(poli_id, db: Session = Depends(get_db)):
    success = delete_poli(db, poli_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poli not found")
    return {"message": "Poli deleted successfully"}