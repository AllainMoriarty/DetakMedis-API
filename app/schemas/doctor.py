from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class DoctorBase(BaseModel):
    name: str
    profile: Optional[str] = None
    speciality: Optional[str] = None
    contact_info: Optional[str] = None
    location: Optional[str] = None
    practice_schedule: Optional[Dict[str, Any]] = None
    poli_id: int

class DoctorCreate(DoctorBase):
    pass

class DoctorUpdate(BaseModel):
    name: Optional[str] = None
    profile: Optional[str] = None
    speciality: Optional[str] = None
    contact_info: Optional[str] = None
    location: Optional[str] = None
    practice_schedule: Optional[Dict[str, Any]] = None
    poli_id: Optional[int] = None

class DoctorResponse(DoctorBase):
    id: int

    class Config:
        from_attributes = True