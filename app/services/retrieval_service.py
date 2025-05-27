from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from app.core.config import settings
from app.models.poli import Poli
from app.models.disease import Disease
from app.models.doctor import Doctor
from app.schemas.chat import ContextDocument
from typing import List, Dict, Any

class RetrievalService:
    async def retrieve_documents(self, db: Session, query_embedding: List[float], top_k: int = settings.SIMILARITY_TOP_K) -> List[ContextDocument]:
        # Retrieves relevant documents from poli, disease, and doctor tables using vector similarity search.
        contexts: List[ContextDocument] = []

        # Retrieve from Poli
        poli_results = db.query(Poli.name, Poli.description, Poli.embedding.l2_distance(query_embedding).label("distance")) \
            .order_by(Poli.embedding.l2_distance(query_embedding)).limit(top_k).all() 

        for poli in poli_results:
            contexts.append(ContextDocument(
                source="poli",
                content=f"Nama Poli: {poli.name}\nDeskripsi: {poli.description}",
                metadata={"id": poli.id if hasattr(poli, 'id') else None, "name": poli.name, "distance": float(poli.distance)}
            ))
        
        disease_results = db.query(Disease.id, Disease.name, Disease.description, Disease.symptoms, Disease.treatment, Disease.embedding.l2_distance(query_embedding).label("distance")) \
            .order_by(Disease.embedding.l2_distance(query_embedding)).limit(top_k).all()
        
        for disease in disease_results:
            content =f"Penyakit: {disease.name}\nDeskripsi: {disease.description}\nGejala: {disease.symptoms}\nPengobatan: {disease.treatment}"
            contexts.append(ContextDocument(
                source="disease",
                content=content,
                metadata={"id": disease.id, "name": disease.name, "distance": float(disease.distance)}
            ))
        
        # Retrieve from Doctor
        doctor_results = db.query(
            Doctor.id, Doctor.name, Doctor.speciality, Doctor.profile, Doctor.location,
            Doctor.practice_schedule, Doctor.embedding.l2_distance(query_embedding).label("distance")
        ).order_by(Doctor.embedding.l2_distance(query_embedding)).limit(top_k).all()

        for doctor in doctor_results:
            content = f"Dokter: {doctor.name}\nSpesialis: {doctor.speciality}\nProfil: {doctor.profile}\nLokasi: {doctor.location}\nJam Kerja: {doctor.practice_schedule}"
            contexts.append(ContextDocument(
                source="doctor",
                content=content,
                metadata={"id": doctor.id, "name": doctor.name, "distance": float(doctor.distance)}
            ))

        return contexts

retrieval_service = RetrievalService()