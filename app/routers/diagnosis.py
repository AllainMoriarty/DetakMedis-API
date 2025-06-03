# app/routers/diagnosis.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Annotated, Optional
import logging
import json
from app.schemas.diagnosis import Diagnosis, DiagnosisCreate, DiagnosisUpdate
from app.services.diagnosis_service import diagnosis_service
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/diagnoses",
    tags=["Diagnoses"],
)

logger = logging.getLogger(__name__)

@router.post("/", response_model=Diagnosis, status_code=status.HTTP_201_CREATED)
async def create_diagnoses(image_file: Annotated[UploadFile, File(description="The medical image file to upload.")],
                              query: str = Form(...), db: Session = Depends(get_db),
                              patient: User = Depends(get_current_user)):
    if image_file.content_type not in ["image/jpeg", "image/png", "image/webp", "image/dicom", "application/dicom"]:
        raise HTTPException(status_code=400, detail="Invalid image type. Allowed: JPEG, PNG, WEBP, DICOM.")
    try:
        diagnosis_data = DiagnosisCreate(
            patient_id=patient.id,
            query=query
        )
        return await diagnosis_service.create_diagnosis(
            db=db,
            image_file=image_file,
            diagnosis_data=diagnosis_data
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception("Failed to create medical image in service.")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/", response_model=List[Diagnosis])
async def get_all_diagnoses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all diagnoses (NO LOGIN REQUIRED - FOR TESTING)"""
    try:
        diagnoses = await diagnosis_service.get_all_diagnosis(db, skip=skip, limit=limit)
        return diagnoses
    except Exception as e:
        logger.exception("Failed to get diagnoses.")
        raise HTTPException(status_code=500, detail=f"Failed to get diagnoses: {str(e)}")

@router.get("/patient/{patient_id}", response_model=List[Diagnosis])
async def get_all_diagnoses_by_patient_id(
    patient_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all diagnoses for specific patient (NO LOGIN REQUIRED)"""
    try:
        diagnoses = await diagnosis_service.get_all_diagnosis_by_patient_id(db, patient_id=patient_id, skip=skip, limit=limit)
        return diagnoses
    except Exception as e:
        logger.exception(f"Failed to get diagnoses for patient {patient_id}.")
        raise HTTPException(status_code=500, detail=f"Failed to get patient diagnoses: {str(e)}")

@router.get("/{diagnosis_id}", response_model=Diagnosis)
def get_diagnoses(
    diagnosis_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get diagnosis by ID"""
    try:
        return diagnosis_service.get_diagnosis_by_id(db, diagnosis_id=diagnosis_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Failed to get diagnosis {diagnosis_id}.")
        raise HTTPException(status_code=500, detail=f"Failed to get diagnosis: {str(e)}")

@router.put("/{diagnosis_id}", response_model=Diagnosis)
async def update_diagnoses(
    diagnosis_id: int,
    image_file: Annotated[Optional[UploadFile], File(description="Optional new medical image file to upload.")] = None,
    query: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update existing diagnosis with optional new image"""
    try:
        if image_file and image_file.content_type not in ["image/jpeg", "image/png", "image/webp", "image/dicom", "application/dicom"]:
            raise HTTPException(status_code=400, detail="Invalid image type. Allowed: JPEG, PNG, WEBP, DICOM.")
        
        diagnosis_update = DiagnosisUpdate(query=query)
        
        return await diagnosis_service.update_diagnosis(
            db=db, 
            diagnosis_id=diagnosis_id, 
            image_file=image_file,
            diagnosis_update=diagnosis_update
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Failed to update diagnosis {diagnosis_id}.")
        raise HTTPException(status_code=500, detail=f"Failed to update diagnosis: {str(e)}")

@router.delete("/{diagnosis_id}", response_model=dict)
def delete_diagnoses(
    diagnosis_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete diagnosis by ID"""
    try:
        return diagnosis_service.delete_diagnosis(db, diagnosis_id=diagnosis_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Failed to delete diagnosis {diagnosis_id}.")
        raise HTTPException(status_code=500, detail=f"Failed to delete diagnosis: {str(e)}")