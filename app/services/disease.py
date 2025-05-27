from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from app.models.disease import Disease
from app.schemas.disease import DiseaseCreate, DiseaseUpdate, DiseaseResponse
from app.services.embedding_service import embedding_service

def get_disease(db: Session, disease_id: int) -> Optional[DiseaseResponse]:
    return db.query(Disease).filter(Disease.id == disease_id).first()

def get_diseases(db: Session) -> List[DiseaseResponse]:
    return db.query(Disease).all()

async def create_disease(db: Session, disease_data: DiseaseCreate) -> DiseaseResponse:
    combined_text = f"{disease_data.name}: {disease_data.description}" if disease_data.description else disease_data.name
    embedding = await embedding_service.get_embedding(combined_text)
    db_disease = Disease(
        name=disease_data.name,
        description=disease_data.description,
        symptoms=disease_data.symptoms,
        treatment=disease_data.treatment,
        poli_id=disease_data.poli_id,
        embedding=embedding
    )
    db.add(db_disease)
    db.commit()
    db.refresh(db_disease)
    return db_disease

async def update_disease(db: Session, disease_id: int, disease_update: DiseaseUpdate) -> Optional[DiseaseResponse]:
    db_disease = db.query(Disease).filter(Disease.id == disease_id).first()
    if not db_disease:
        return None
    
    update_data = disease_update.model_dump(exclude_unset=True)

    should_update_embedding = "name" in update_data or "description" in update_data
    if should_update_embedding:
        new_name = update_data.get("name", db_disease.name)
        new_description = update_data.get("description", db_disease.description)
        combined_text = f"{new_name}: {new_description}"
        embedding = await embedding_service.get_embedding(combined_text)
        update_data["embedding"] = embedding

    for field, value in update_data.items():
        setattr(db_disease,field, value)
    
    db.commit()
    db.refresh(db_disease)
    return db_disease

def delete_disease(db: Session, disease_id: int) -> bool:
    db_disease = db.query(Disease).filter(Disease.id == disease_id).first()
    if not db_disease:
        return False
    
    db.delete(db_disease)
    db.commit()
    return True