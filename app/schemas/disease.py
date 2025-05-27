from pydantic import BaseModel
from typing import Optional, List

class DiseaseBase(BaseModel):
    name: str
    description: Optional[str] = None
    symptoms: Optional[str] = None
    treatment: Optional[str] = None
    poli_id: int

class DiseaseCreate(DiseaseBase):
    pass

class DiseaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    symptoms: Optional[str] = None
    treatment: Optional[str] = None
    poli_id: int

class DiseaseResponse(DiseaseBase):
    id: int

    class Config:
        from_attributes = True