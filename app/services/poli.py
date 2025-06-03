from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from app.models.poli import Poli
from app.schemas.poli import PoliCreate, PoliUpdate, PoliResponse
from app.services.embedding_service import embedding_service

def get_poli(db: Session, poli_id: int) -> Optional[PoliResponse]:
    return db.query(Poli).filter(Poli.id == poli_id).first()

def get_polis(db: Session) -> List[PoliResponse]:
    return db.query(Poli).all()

async def create_poli(db: Session, poli_data: PoliCreate) -> PoliResponse:
    combined_text = f"{poli_data.name}: {poli_data.description}" if poli_data.description else poli_data.name
    embedding = await embedding_service.get_embedding(combined_text)
    db_poli = Poli(
        name=poli_data.name,
        description=poli_data.description,
        embedding=embedding
    )
    db.add(db_poli)
    db.commit()
    db.refresh(db_poli)
    return db_poli

async def update_poli(db: Session, poli_id: int, poli_update: PoliUpdate) -> Optional[PoliResponse]:
    db_poli = db.query(Poli).filter(Poli.id == poli_id).first()
    if not db_poli:
        return None
    
    update_data = poli_update.model_dump(exclude_unset=True)

    should_update_embedding = "name" in update_data or "description" in update_data
    if should_update_embedding:
        new_name = update_data.get("name", db_poli.name)
        new_description = update_data.get("description", db_poli.description)
        combined_text = f"{new_name}: {new_description}"
        embedding = await embedding_service.get_embedding(combined_text)
        update_data["embedding"] = embedding
        
    for field, value in update_data.items():
        setattr(db_poli, field, value)

    db.commit()
    db.refresh(db_poli)
    return db_poli

def delete_poli(db: Session, poli_id: int) -> bool:
    db_poli = db.query(Poli).filter(Poli.id == poli_id).first()
    if not db_poli:
        return None
    
    db.delete(db_poli)
    db.commit()
    return True