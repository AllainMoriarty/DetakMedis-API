from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.disease import get_disease, get_diseases, create_disease, update_disease, delete_disease
from app.schemas.disease import DiseaseCreate,DiseaseUpdate, DiseaseResponse

router = APIRouter(prefix="/disease", tags=["disease"])

@router.post("/", response_model=DiseaseResponse)
async def create(poli: DiseaseCreate, db: Session = Depends(get_db)):
    return await create_disease(db, poli)

@router.get("/", response_model=List[DiseaseResponse])
def get_all(db: Session = Depends(get_db)):
    return get_diseases(db)

@router.get("/{disease_id}", response_model=DiseaseResponse)
def get_by_id(disease_id: int, db: Session = Depends(get_db)):
    disease = get_disease(db, disease_id)
    if not disease:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disease not found")
    
    return disease

@router.put("/{disease_id}", response_model=DiseaseResponse)
async def update(disease_id: int, disease: DiseaseUpdate, db: Session = Depends(get_db)):
    updated = await update_disease(db, disease_id, disease)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disease not found")
    
    return updated

@router.delete("/{disease_id}")
def delete(disease_id, db: Session = Depends(get_db)):
    success = delete_disease(db, disease_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disease not found")
    return {"message": "Disease deleted successfully"}