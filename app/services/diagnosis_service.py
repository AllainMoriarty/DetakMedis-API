# app/services/diagnosis_service.py
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.models.diagnosis import Diagnosis
from app.services.embedding_service import embedding_service
from app.services.aidoc_service import aidoc_service
from app.services.retrieval_service import retrieval_service
from app.schemas.chat import ChatRequest, ChatResponse, ContextDocument
from app.schemas.medical_image import MedicalImageCreate, MedicalImageUpdate
from app.schemas.diagnosis import DiagnosisCreate, DiagnosisUpdate
from app.services.vision_model_service import vision_model_service
from app.services.medical_image_service import medical_image_service
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class DiagnosisService:
    async def create_diagnosis(self, db: Session, image_file: UploadFile, diagnosis_data: DiagnosisCreate):
        medical_image_data = MedicalImageCreate(
            patient_id=diagnosis_data.patient_id,
        )

        medical_image = await medical_image_service.create_medical_image_with_file(db, medical_image_data, image_file)

        query_embedding = await embedding_service.get_embedding(diagnosis_data.query)
        retrieved_docs_from_db = await retrieval_service.retrieve_documents(db, query_embedding)

        retrieved_docs_pydantic: List[ContextDocument] = []
        if retrieved_docs_from_db:
            for doc_db in retrieved_docs_from_db:
                retrieved_docs_pydantic.append(ContextDocument(source=getattr(doc_db, 'source', 'Unknown'),
                                        content=getattr(doc_db, 'content', ''),
                                        metadata=getattr(doc_db, 'metadata', {})))

        disease_id = None
        for doc in retrieved_docs_pydantic:
            if doc.source == "disease" and "id" in doc.metadata:
                disease_id = doc.metadata["id"]
                break

        related_doctors = []
        for doc in retrieved_docs_pydantic:
            if doc.source == "doctor":
                related_doctors.append({
                    "id": doc.metadata.get("id"),
                    "name": doc.metadata.get("name"),
                    "speciality": doc.content.split("\n")[1].replace("Spesialis: ", ""),
                    "location": doc.content.split("\n")[2].replace("Lokasi: ", ""),
                    "practice_schedule": doc.content.split("\n")[3].replace("Jam Kerja: ", "")
                })

        retrieved_docs_context_str = "\n\n".join([f"Sumber Dokumen: {doc.source}\nKonten Dokumen: {doc.content}" for doc in retrieved_docs_pydantic])
        if not retrieved_docs_pydantic:
            retrieved_docs_context_str = "tidak ada informasi dokumen relevan yang ditemukan di database."

        final_context_parts = []
        if medical_image:
            final_context_parts.append(medical_image.label)

        final_context_parts.append("INFORMASI DOKUMEN TEKSTUAL TENTANG KELUHAN PENGGUNA (dari database):\n" + retrieved_docs_context_str)

        context_str = "\n\n---\n\n".join(final_context_parts)

        answer = await aidoc_service.generate_response(question=diagnosis_data.query, context=context_str)

        db_diagnosis = Diagnosis(
            query=diagnosis_data.query,
            result=answer,
            disease_id=disease_id,
            medical_image_id=medical_image.id
        )

        db.add(db_diagnosis)
        db.commit()
        db.refresh(db_diagnosis)

        return {
            "id": db_diagnosis.id,
            "path": medical_image.path,
            "query": diagnosis_data.query,
            "result": answer,
            "related_doctors": related_doctors
        }
    
    async def get_all_diagnosis(self, db: Session, skip: int = 0, limit: int = 100):
        """Get all diagnoses with complete information"""
        try:
            from app.models.medical_image import MedicalImage
            
            diagnoses = (db.query(Diagnosis)
                        .join(MedicalImage, Diagnosis.medical_image_id == MedicalImage.id)
                        .offset(skip)
                        .limit(limit)
                        .all())
            
            result = []
            for diagnosis in diagnoses:
                # Get related doctors
                query_embedding = await embedding_service.get_embedding(diagnosis.query)
                retrieved_docs_from_db = await retrieval_service.retrieve_documents(db, query_embedding)

                related_doctors = []
                if retrieved_docs_from_db:
                    for doc_db in retrieved_docs_from_db:
                        if getattr(doc_db, 'source', '') == "doctor":
                            content = getattr(doc_db, 'content', '')
                            metadata = getattr(doc_db, 'metadata', {})
                            
                            # Parse content to extract doctor info
                            content_lines = content.split("\n")
                            related_doctors.append({
                                "id": metadata.get("id"),
                                "name": metadata.get("name"),
                                "speciality": content_lines[1].replace("Spesialis: ", "") if len(content_lines) > 1 else "",
                                "location": content_lines[2].replace("Lokasi: ", "") if len(content_lines) > 2 else "",
                                "practice_schedule": content_lines[3].replace("Jam Kerja: ", "") if len(content_lines) > 3 else ""
                            })
                
                result.append({
                    "id": diagnosis.id,
                    "path": diagnosis.medical_image.path if diagnosis.medical_image else "",
                    "query": diagnosis.query,
                    "result": diagnosis.result,
                    "related_doctors": related_doctors
                })
            
            return result
        except Exception as e:
            logger.error(f"Error getting all diagnoses: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get diagnoses: {str(e)}")
    
    async def get_all_diagnosis_by_patient_id(self, db: Session, patient_id: int, skip: int = 0, limit: int = 100):
        """Get all diagnoses by patient_id with complete information"""
        try:
            from app.models.medical_image import MedicalImage
            
            diagnoses = (db.query(Diagnosis)
                        .join(MedicalImage, Diagnosis.medical_image_id == MedicalImage.id)
                        .filter(MedicalImage.patient_id == patient_id)
                        .offset(skip)
                        .limit(limit)
                        .all())
            
            result = []
            for diagnosis in diagnoses:
                # Get related doctors
                query_embedding = await embedding_service.get_embedding(diagnosis.query)
                retrieved_docs_from_db = await retrieval_service.retrieve_documents(db, query_embedding)

                related_doctors = []
                if retrieved_docs_from_db:
                    for doc_db in retrieved_docs_from_db:
                        if getattr(doc_db, 'source', '') == "doctor":
                            content = getattr(doc_db, 'content', '')
                            metadata = getattr(doc_db, 'metadata', {})
                            
                            # Parse content to extract doctor info
                            content_lines = content.split("\n")
                            related_doctors.append({
                                "id": metadata.get("id"),
                                "name": metadata.get("name"),
                                "speciality": content_lines[1].replace("Spesialis: ", "") if len(content_lines) > 1 else "",
                                "location": content_lines[2].replace("Lokasi: ", "") if len(content_lines) > 2 else "",
                                "practice_schedule": content_lines[3].replace("Jam Kerja: ", "") if len(content_lines) > 3 else ""
                            })
                
                result.append({
                    "id": diagnosis.id,
                    "path": diagnosis.medical_image.path if diagnosis.medical_image else "",
                    "query": diagnosis.query,
                    "result": diagnosis.result,
                    "related_doctors": related_doctors
                })
            
            return result
        except Exception as e:
            logger.error(f"Error getting diagnoses for patient {patient_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get patient diagnoses: {str(e)}")
    
    async def get_diagnosis_by_id(self, db: Session, diagnosis_id: int):
        """Get diagnosis by ID with complete information"""
        try:
            from app.models.medical_image import MedicalImage
            
            diagnosis = (db.query(Diagnosis)
                        .join(MedicalImage, Diagnosis.medical_image_id == MedicalImage.id)
                        .filter(Diagnosis.id == diagnosis_id)
                        .first())
            
            if not diagnosis:
                raise HTTPException(status_code=404, detail="Diagnosis not found")
            
            # Get related doctors
            query_embedding = await embedding_service.get_embedding(diagnosis.query)
            retrieved_docs_from_db = await retrieval_service.retrieve_documents(db, query_embedding)

            related_doctors = []
            if retrieved_docs_from_db:
                for doc_db in retrieved_docs_from_db:
                    if getattr(doc_db, 'source', '') == "doctor":
                        content = getattr(doc_db, 'content', '')
                        metadata = getattr(doc_db, 'metadata', {})
                        
                        # Parse content to extract doctor info
                        content_lines = content.split("\n")
                        related_doctors.append({
                            "id": metadata.get("id"),
                            "name": metadata.get("name"),
                            "speciality": content_lines[1].replace("Spesialis: ", "") if len(content_lines) > 1 else "",
                            "location": content_lines[2].replace("Lokasi: ", "") if len(content_lines) > 2 else "",
                            "practice_schedule": content_lines[3].replace("Jam Kerja: ", "") if len(content_lines) > 3 else ""
                        })
            
            return {
                "id": diagnosis.id,
                "path": diagnosis.medical_image.path if diagnosis.medical_image else "",
                "query": diagnosis.query,
                "result": diagnosis.result,
                "related_doctors": related_doctors
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting diagnosis {diagnosis_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get diagnosis: {str(e)}")
    
    async def update_diagnosis(self, db: Session, diagnosis_id: int, image_file: Optional[UploadFile], diagnosis_update: DiagnosisUpdate):
        """Update diagnosis with optional new image - similar to create process"""
        try:
            # Get existing diagnosis
            diagnosis = db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
            if not diagnosis:
                raise HTTPException(status_code=404, detail="Diagnosis not found")
            
            # Get current medical image
            from app.models.medical_image import MedicalImage
            current_medical_image = db.query(MedicalImage).filter(MedicalImage.id == diagnosis.medical_image_id).first()
            
            if not current_medical_image:
                raise HTTPException(status_code=404, detail="Associated medical image not found")
            
            medical_image = current_medical_image
            
            # If new image is provided, create new medical image
            if image_file:
                medical_image_data = MedicalImageCreate(
                    patient_id=current_medical_image.patient_id,
                )
                medical_image = await medical_image_service.create_medical_image_with_file(db, medical_image_data, image_file)
            
            # Use updated query or keep existing
            query = diagnosis_update.query if diagnosis_update.query is not None else diagnosis.query
            
            # Re-process the diagnosis with new/existing image and query
            query_embedding = await embedding_service.get_embedding(query)
            retrieved_docs_from_db = await retrieval_service.retrieve_documents(db, query_embedding)

            retrieved_docs_pydantic: List[ContextDocument] = []
            if retrieved_docs_from_db:
                for doc_db in retrieved_docs_from_db:
                    retrieved_docs_pydantic.append(ContextDocument(source=getattr(doc_db, 'source', 'Unknown'),
                                            content=getattr(doc_db, 'content', ''),
                                            metadata=getattr(doc_db, 'metadata', {})))

            disease_id = None
            for doc in retrieved_docs_pydantic:
                if doc.source == "disease" and "id" in doc.metadata:
                    disease_id = doc.metadata["id"]
                    break

            related_doctors = []
            for doc in retrieved_docs_pydantic:
                if doc.source == "doctor":
                    related_doctors.append({
                        "id": doc.metadata.get("id"),
                        "name": doc.metadata.get("name"),
                        "speciality": doc.content.split("\n")[1].replace("Spesialis: ", ""),
                        "location": doc.content.split("\n")[2].replace("Lokasi: ", ""),
                        "practice_schedule": doc.content.split("\n")[3].replace("Jam Kerja: ", "")
                    })

            retrieved_docs_context_str = "\n\n".join([f"Sumber Dokumen: {doc.source}\nKonten Dokumen: {doc.content}" for doc in retrieved_docs_pydantic])
            if not retrieved_docs_pydantic:
                retrieved_docs_context_str = "tidak ada informasi dokumen relevan yang ditemukan di database."

            final_context_parts = []
            if medical_image:
                final_context_parts.append(medical_image.label)

            final_context_parts.append("INFORMASI DOKUMEN TEKSTUAL TENTANG KELUHAN PENGGUNA (dari database):\n" + retrieved_docs_context_str)

            context_str = "\n\n---\n\n".join(final_context_parts)

            answer = await aidoc_service.generate_response(question=query, context=context_str)
            
            # Update diagnosis fields
            diagnosis.query = query
            diagnosis.result = answer
            diagnosis.disease_id = disease_id
            diagnosis.medical_image_id = medical_image.id
            
            db.commit()
            db.refresh(diagnosis)
            
            return {
                "id": diagnosis.id,
                "path": medical_image.path,
                "query": diagnosis.query,
                "result": diagnosis.result,
                "related_doctors": related_doctors
            }
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating diagnosis {diagnosis_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to update diagnosis: {str(e)}")
    
    async def delete_diagnosis(self, db: Session, diagnosis_id: int):
        """Delete diagnosis and return the same format as other methods"""
        try:
            from app.models.medical_image import MedicalImage
            
            diagnosis = (db.query(Diagnosis)
                        .join(MedicalImage, Diagnosis.medical_image_id == MedicalImage.id)
                        .filter(Diagnosis.id == diagnosis_id)
                        .first())
            
            if not diagnosis:
                raise HTTPException(status_code=404, detail="Diagnosis not found")
            
            # Get related doctors
            query_embedding = await embedding_service.get_embedding(diagnosis.query)
            retrieved_docs_from_db = await retrieval_service.retrieve_documents(db, query_embedding)

            related_doctors = []
            if retrieved_docs_from_db:
                for doc_db in retrieved_docs_from_db:
                    if getattr(doc_db, 'source', '') == "doctor":
                        content = getattr(doc_db, 'content', '')
                        metadata = getattr(doc_db, 'metadata', {})
                        
                        # Parse content to extract doctor info
                        content_lines = content.split("\n")
                        related_doctors.append({
                            "id": metadata.get("id"),
                            "name": metadata.get("name"),
                            "speciality": content_lines[1].replace("Spesialis: ", "") if len(content_lines) > 1 else "",
                            "location": content_lines[2].replace("Lokasi: ", "") if len(content_lines) > 2 else "",
                            "practice_schedule": content_lines[3].replace("Jam Kerja: ", "") if len(content_lines) > 3 else ""
                        })
            
            # Store data before deletion
            result_data = {
                "id": diagnosis.id,
                "path": diagnosis.medical_image.path if diagnosis.medical_image else "",
                "query": diagnosis.query,
                "result": diagnosis.result,
                "related_doctors": related_doctors,
                "message": "Diagnosis successfully deleted"
            }
            
            db.delete(diagnosis)
            db.commit()
            
            return result_data
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting diagnosis {diagnosis_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to delete diagnosis: {str(e)}")

diagnosis_service = DiagnosisService()