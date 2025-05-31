# app/routers/medical_image_router.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Annotated
import logging
import json
from pydantic import ValidationError
from app.schemas.medical_image import MedicalImage, MedicalImageUpdate, MedicalImageCreate
from app.services.medical_image_service import medical_image_service
from app.core.database import get_db

router = APIRouter(
    prefix="/medical-images",
    tags=["Medical Images"]
)
logger = logging.getLogger(__name__)

@router.post("/", response_model=MedicalImage, status_code=201)
async def create_medical_image(
    image_file: Annotated[UploadFile, File(description="The medical image file to upload.")],
    medical_image: str = Form(...),
    db: Session = Depends(get_db)
):
    if image_file.content_type not in ["image/jpeg", "image/png", "image/webp", "image/dicom", "application/dicom"]:
        raise HTTPException(status_code=400, detail="Invalid image type. Allowed: JPEG, PNG, WEBP, DICOM.")

    try:
        medical_image_data = MedicalImageCreate(**json.loads(medical_image))
        return await medical_image_service.create_medical_image_with_file(
            db=db,
            medical_image_data=medical_image_data,
            image_file=image_file
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception("Failed to create medical image in service.")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/{image_id}/predict/", response_model=Dict[str, float])
async def predict_from_medical_image(
    image_id: int,
    db: Session = Depends(get_db)
):
    try:
        predictions = await medical_image_service.run_prediction_on_image(image_id=image_id, db=db)
        return predictions
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Failed to run prediction on image {image_id}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during prediction: {str(e)}")

@router.get("/{image_id}", response_model=MedicalImage)
def read_medical_image(image_id: int, db: Session = Depends(get_db)):
    db_image = medical_image_service.get_medical_image(db, image_id=image_id)
    if db_image is None:
        raise HTTPException(status_code=404, detail="Medical image not found")
    return db_image

@router.get("/patient/{patient_id}", response_model=List[MedicalImage])
def read_medical_images_by_patient(patient_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    images = medical_image_service.get_medical_images_by_patient(db, patient_id=patient_id, skip=skip, limit=limit)
    return images

@router.get("/", response_model=List[MedicalImage])
def read_all_medical_images(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    images = medical_image_service.get_all_medical_images(db, skip=skip, limit=limit)
    return images

@router.put("/{image_id}", response_model=MedicalImage)
async def update_medical_image(
    image_id: int,
    image_file: Annotated[UploadFile, File(description="The new medical image file to upload.")],
    medical_image: str = Form(...),
    db: Session = Depends(get_db)
):
    if image_file.content_type not in ["image/jpeg", "image/png", "image/webp", "image/dicom", "application/dicom"]:
        raise HTTPException(status_code=400, detail="Invalid image type. Allowed: JPEG, PNG, WEBP, DICOM.")

    try:
        medical_image_data = MedicalImageUpdate(**json.loads(medical_image))
        return await medical_image_service.update_medical_image(
            db=db,
            image_id=image_id,
            medical_image_data=medical_image_data,
            image_file=image_file
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Failed to update medical image {image_id} with new file.")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.delete("/{image_id}", response_model=MedicalImage)
def delete_medical_image(image_id: int, db: Session = Depends(get_db)):
    db_image = medical_image_service.delete_medical_image(db, image_id=image_id)
    if db_image is None:
        raise HTTPException(status_code=404, detail="Medical image not found")
    return db_image