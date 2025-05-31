from pydantic import BaseModel, Field
from typing import Optional

class MedicalImageBase(BaseModel):
    patient_id: int = Field(..., description="ID of the patient")

class MedicalImageCreate(MedicalImageBase):
    pass

class MedicalImageUpdate(BaseModel):
    patient_id: Optional[int] = None

class MedicalImage(MedicalImageBase):
    id: int = Field(..., description="Unique ID of the medical image")

    class Config:
        from_attributes = True