from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base

class Diagnosis(Base):
    __tablename__ = "diagnosis"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    result = Column(Text, nullable=False)
    disease_info = Column(Text, nullable=False)
    disease_id = Column(Integer, ForeignKey("disease.id", onupdate="CASCADE", ondelete="SET NULL"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id", onupdate="CASCADE", ondelete="SET NULL"), nullable=False)
    medical_image_id = Column(Integer, ForeignKey("medical_image.id", onupdate="CASCADE", ondelete="SET NULL"), unique=True, nullable=False)
    embedding = Column(Vector(384), nullable=True)

    # Relation to Disease
    disease = relationship("Disease", foreign_keys=[disease_id], back_populates="diagnosis")

    # Relation to Doctor
    doctor = relationship("Doctor", foreign_keys=[doctor_id], back_populates="diagnosis")

    # Relation to Medical Image
    medical_image = relationship("MedicalImage", foreign_keys=[medical_image_id], back_populates="diagnosis")