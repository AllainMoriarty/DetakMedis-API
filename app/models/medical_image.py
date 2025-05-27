from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.security import Base

class MedicalImage(Base):
    __tablename__ = "medical_images"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    path = Column(String, nullable=False)
    label = Column(String, nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"), nullable=False)
    poli_id = Column(Integer, ForeignKey("poli.id", onupdate="CASCADE", ondelete="SET NULL"), nullable=False)

    # Relation to Patient
    patient = relationship("User", foreign_keys=[patient_id], back_populates="medical_image")

    # Relation to Poli
    poli = relationship("Poli", foreign_keys=[poli_id], back_populates="medical_image")

    # Relation to Diagnosis
    diagnosis = relationship("Diagnosis", back_populates="medical_image", uselist=False)