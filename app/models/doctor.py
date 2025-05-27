from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship
from app.core.database import Base

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    profile = Column(String)
    speciality = Column(String, index=True, nullable=True)
    contact_info = Column(String)
    location = Column(String)
    practice_schedule = Column(JSON, nullable=True)
    poli_id = Column(Integer, ForeignKey("poli.id", onupdate="CASCADE", ondelete="SET NULL"), nullable=False)
    embedding = Column(Vector(768), nullable=True)

    # Relation to Poli
    poli = relationship("Poli", foreign_keys=[poli_id], back_populates="doctor")