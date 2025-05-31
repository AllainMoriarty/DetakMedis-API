from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.schemas.medical_image import MedicalImageBase

class DiagnosisBase(BaseModel):
    query: str

class DiagnosisCreate(DiagnosisBase, MedicalImageBase):
    pass

class DiagnosisUpdate(BaseModel):
    query: Optional[str] = None

class Diagnosis(DiagnosisBase):
    id: int
    path: str
    result: str
    related_doctors: List[Dict[str, Any]]

    class Config:
        from_attributes = True