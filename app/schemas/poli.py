from pydantic import BaseModel
from typing import Optional, List

class PoliBase(BaseModel):
    name: str
    description: Optional[str] = None

class PoliCreate(PoliBase):
    pass

class PoliUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class PoliResponse(PoliBase):
    id: int

    class Config:
        from_attributes = True