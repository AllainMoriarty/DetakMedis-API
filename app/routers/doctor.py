from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.doctor import get_doctor, get_doctors, create_doctor, update_doctor, delete_doctor
from app.schemas.doctor import DoctorCreate, DoctorUpdate, DoctorResponse

router = APIRouter(prefix="/doctor", tags=["doctor"])

@router.post("/", response_model=DoctorResponse)
async def create(doctor: DoctorCreate, db: Session = Depends(get_db)):
    return await create_doctor(db, doctor)

@router.get("/", response_model=List[DoctorResponse])
def get_all(db: Session = Depends(get_db)):
    return get_doctors(db)

@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_by_id(doctor_id: int, db: Session = Depends(get_db)):
    doctor = get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    
    return doctor

@router.put("/{doctor_id}", response_model=DoctorResponse)
async def update(doctor_id: int, doctor: DoctorUpdate, db: Session = Depends(get_db)):
    updated = await update_doctor(db, doctor_id, doctor)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    
    return updated

@router.delete("/{doctor_id}")
def delete(doctor_id, db: Session = Depends(get_db)):
    success = delete_doctor(db, doctor_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    return {"message": "doctor deleted successfully"}