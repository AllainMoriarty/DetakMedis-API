from sqlalchemy import Column, Integer, String, Text, ForeignKey
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship
from app.core.database import Base

class Disease(Base):
    __tablename__ = "disease"

    id = Column(Integer, primary_key=True, index=False, nullable=False)
    name = Column(String, index=True, nullable=False)
    description = Column(String, index=True)
    symptoms = Column(Text)
    treatment = Column(Text)
    poli_id = Column(Integer, ForeignKey("poli.id", onupdate="CASCADE", ondelete="SET NULL"), nullable=False)
    embedding = Column(Vector(768), nullable=True)

    # Relation to Poli
    poli = relationship("Poli", foreign_keys=[poli_id], back_populates="disease")