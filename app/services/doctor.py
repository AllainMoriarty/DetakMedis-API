from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorUpdate, DoctorResponse
from app.services.embedding_service import embedding_service

def get_doctor(db: Session, doctor_id: int) -> Optional[DoctorResponse]:
    return db.query(Doctor).filter(Doctor.id == doctor_id).first()

def get_doctors(db: Session) -> List[DoctorResponse]:
    return db.query(Doctor).all()

def get_doctors_by_poli_id(db: Session, poli_id: int) -> List[DoctorResponse]:
    """
    Get all doctors by poli_id
    """
    return db.query(Doctor).filter(Doctor.poli_id == poli_id).all()

async def create_doctor(db: Session, doctor_data: DoctorCreate) -> DoctorResponse:
    combined_text = f"{doctor_data.name} {doctor_data.speciality or ''} {doctor_data.profile or ''}".strip()
    embedding = await embedding_service.get_embedding(combined_text)
    db_doctor = Doctor(
        name=doctor_data.name,
        profile=doctor_data.profile,
        speciality=doctor_data.speciality,
        contact_info=doctor_data.contact_info,
        location=doctor_data.location,
        practice_schedule=doctor_data.practice_schedule,
        poli_id=doctor_data.poli_id,
        embedding=embedding
    )
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

async def update_doctor(db: Session, doctor_id: int, doctor_update: DoctorUpdate) -> Optional[DoctorResponse]:
    db_doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not db_doctor:
        return None
    
    update_data = doctor_update.model_dump(exclude_unset=True)

    should_regenerate = any(
        field in update_data for field in ["name", "speciality", "profile"]
    )

    if should_regenerate:
        combined_text = (
            f"{update_data.get('name', db_doctor.name)} "
            f"{update_data.get('speciality', db_doctor.speciality) or ''} "
            f"{update_data.get('profile', db_doctor.profile) or ''}"
        ).strip()
        embedding = await embedding_service.get_embedding(combined_text)
        update_data["embedding"] = embedding
        
    for field, value in update_data.items():
        setattr(db_doctor, field, value)

    db.commit()
    db.refresh(db_doctor)
    return db_doctor

def delete_doctor(db: Session, doctor_id: int) -> bool:
    db_doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not db_doctor:
        return False
    
    db.delete(db_doctor)
    db.commit()
    return True