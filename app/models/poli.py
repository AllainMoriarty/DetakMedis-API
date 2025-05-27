from sqlalchemy import Column, Integer, String
from pgvector.sqlalchemy import Vector
from app.core.database import Base
from sqlalchemy.orm import relationship

class Poli(Base):
    __tablename__ = "poli"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    description = Column(String)
    embedding = Column(Vector(768), nullable=True)
    
    disease = relationship("Disease", foreign_keys="[Disease.poli_id]", back_populates="poli")
    doctor = relationship("Doctor", foreign_keys="[Doctor.poli_id]", back_populates="poli")