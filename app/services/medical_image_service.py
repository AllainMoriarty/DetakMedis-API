# app/services/medical_image_service.py
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status
import shutil
import os
from typing import List, Optional, Dict
import uuid
import logging
from app.models.medical_image import MedicalImage as MedicalImageModel
from app.schemas.medical_image import MedicalImageCreate, MedicalImageUpdate
from app.services.vision_model_service import vision_model_service 
from app.core.config import settings 

logger = logging.getLogger(__name__)

class MedicalImageService:
    def get_medical_image(self, db: Session, image_id: int) -> Optional[MedicalImageModel]:
        return db.query(MedicalImageModel).filter(MedicalImageModel.id == image_id).first()

    def get_medical_images_by_patient(self, db: Session, patient_id: int, skip: int = 0, limit: int = 100) -> List[MedicalImageModel]:
        return db.query(MedicalImageModel).filter(MedicalImageModel.patient_id == patient_id).offset(skip).limit(limit).all()

    def get_all_medical_images(self, db: Session, skip: int = 0, limit: int = 100) -> List[MedicalImageModel]:
        return db.query(MedicalImageModel).offset(skip).limit(limit).all()

    async def create_medical_image_with_file(
        self,
        db: Session,
        medical_image_data: MedicalImageCreate,
        image_file: UploadFile
    ) -> MedicalImageModel:
        upload_dir = settings.UPLOAD_IMAGE_DIR
        os.makedirs(upload_dir, exist_ok=True)

        file_extension = image_file.filename.split(".")[-1] if "." in image_file.filename else "png"
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image_file.file, buffer)
            logger.info(f"Image {unique_filename} saved to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save image {unique_filename}: {e}")
            if os.path.exists(file_path): 
                os.remove(file_path)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not save image file.")
        finally:
            await image_file.close()
        
        prediction_source_used = False
        final_label_for_db = None

        try:
            with open(file_path, "rb") as f_img:
                image_bytes_for_prediction = f_img.read()
            
            predictions = await vision_model_service.predict_disease_probabilities(image_data=image_bytes_for_prediction)
            
            if predictions:
                highest_prob_label = max(predictions, key=predictions.get, default=None)
                if highest_prob_label:
                    final_label_for_db = highest_prob_label
                    prediction_source_used = True
                    logger.info(f"Prediction for {unique_filename} successful. Using predicted label: {final_label_for_db}")
            
            if not prediction_source_used:
                if final_label_for_db is not None:
                    logger.info(f"Prediction failed or no clear result for {unique_filename}. Using user-provided label: {final_label_for_db}")
                else:
                    logger.warning(f"Prediction failed/ambiguous for {unique_filename}, and no user label was provided.")
        except Exception as e:
            logger.error(f"Error during prediction for {unique_filename}: {e}. Will use user label if available.")
        
        # --- INTI VALIDASI LABEL (Harus Tetap Ada) ---
        if final_label_for_db is None:
            logger.error(f"Critical: Label for {unique_filename} is None. Cannot save to database.")
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"Cleaned up image {file_path} due to missing label.")
                except Exception as e_rm:
                    logger.error(f"Failed to clean up image {file_path}: {e_rm}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image label is required but could not be determined or provided."
            )

        db_image = MedicalImageModel(
            patient_id=medical_image_data.patient_id,
            poli_id=(1 if final_label_for_db == 'Cardiomegaly' else 2), 
            path=file_path, 
            label=final_label_for_db
        )
        
        try:
            db.add(db_image)
            db.commit()
            db.refresh(db_image)
            logger.info(f"Medical image record created: ID {db_image.id}, Label '{db_image.label}', Path '{db_image.path}'")
            return db_image
        except Exception as e:
            db.rollback()
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e_rm:
                    logger.error(f"Failed to clean up image {file_path} after DB error: {e_rm}")
            logger.error(f"DB error for medical image {unique_filename}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not save medical image metadata to database.")

    async def run_prediction_on_image(self, image_id: int, db: Session) -> Optional[Dict[str, float]]:
        db_image = self.get_medical_image(db=db, image_id=image_id)
        if not db_image:
            raise HTTPException(status_code=404, detail=f"Medical image with ID {image_id} not found.")
        
        if not os.path.exists(db_image.path):
            logger.error(f"Image file not found at path: {db_image.path} for image_id: {image_id}")
            raise HTTPException(status_code=404, detail=f"Image file not found for image ID {image_id} at path {db_image.path}")

        try:
            with open(db_image.path, "rb") as f:
                image_bytes = f.read()
            predictions = await vision_model_service.predict_disease_probabilities(image_data=image_bytes)
            return predictions
        except Exception as e:
            logger.error(f"Error running prediction for image_id {image_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Could not run prediction: {e}")

    async def update_medical_image(
        self,
        db: Session,
        image_id: int,
        medical_image_data: MedicalImageUpdate,
        image_file: UploadFile
    ) -> Optional[MedicalImageModel]:
        # Ambil data image yang ada
        db_image = self.get_medical_image(db=db, image_id=image_id)
        if not db_image:
            raise HTTPException(status_code=404, detail=f"Medical image with ID {image_id} not found.")
        
        # Simpan path file lama untuk dihapus nanti
        old_file_path = db_image.path
        
        upload_dir = settings.UPLOAD_IMAGE_DIR
        os.makedirs(upload_dir, exist_ok=True)

        # Generate nama file baru
        file_extension = image_file.filename.split(".")[-1] if "." in image_file.filename else "png"
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        new_file_path = os.path.join(upload_dir, unique_filename)

        try:
            # Simpan file baru
            with open(new_file_path, "wb") as buffer:
                shutil.copyfileobj(image_file.file, buffer)
            logger.info(f"New image {unique_filename} saved to {new_file_path}")
        except Exception as e:
            logger.error(f"Failed to save new image {unique_filename}: {e}")
            if os.path.exists(new_file_path):
                os.remove(new_file_path)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not save new image file.")
        finally:
            await image_file.close()
        
        prediction_source_used = False
        final_label_for_db = None

        try:
            # Lakukan prediksi dengan gambar baru
            with open(new_file_path, "rb") as f_img:
                image_bytes_for_prediction = f_img.read()
            
            predictions = await vision_model_service.predict_disease_probabilities(image_data=image_bytes_for_prediction)
            
            if predictions:
                highest_prob_label = max(predictions, key=predictions.get, default=None)
                if highest_prob_label:
                    final_label_for_db = highest_prob_label
                    prediction_source_used = True
                    logger.info(f"Prediction for updated image {unique_filename} successful. Using predicted label: {final_label_for_db}")
            
            if not prediction_source_used:
                if final_label_for_db is not None:
                    logger.info(f"Prediction failed or no clear result for updated image {unique_filename}. Using existing label.")
                else:
                    logger.warning(f"Prediction failed/ambiguous for updated image {unique_filename}. Keeping existing label.")
                    final_label_for_db = db_image.label  # Gunakan label yang ada jika prediksi gagal
        except Exception as e:
            logger.error(f"Error during prediction for updated image {unique_filename}: {e}. Will keep existing label.")
            final_label_for_db = db_image.label  # Gunakan label yang ada jika prediksi error
        
        # Validasi label
        if final_label_for_db is None:
            logger.error(f"Critical: Label for updated image {unique_filename} is None. Cannot update database.")
            if os.path.exists(new_file_path):
                try:
                    os.remove(new_file_path)
                    logger.info(f"Cleaned up new image {new_file_path} due to missing label.")
                except Exception as e_rm:
                    logger.error(f"Failed to clean up new image {new_file_path}: {e_rm}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image label is required but could not be determined."
            )

        try:
            # Update database dengan path baru, label baru, dan poli_id baru
            if medical_image_data.patient_id is not None:
                db_image.patient_id = medical_image_data.patient_id
            
            db_image.path = new_file_path
            db_image.label = final_label_for_db
            db_image.poli_id = (1 if final_label_for_db == 'Cardiomegaly' else 2)
            
            db.commit()
            db.refresh(db_image)
            
            # Hapus file lama setelah update berhasil
            if os.path.exists(old_file_path):
                try:
                    os.remove(old_file_path)
                    logger.info(f"Successfully deleted old image file: {old_file_path}")
                except OSError as e:
                    logger.error(f"Error deleting old file {old_file_path}: {e}")
            
            logger.info(f"Medical image record updated: ID {db_image.id}, New Label '{db_image.label}', New Path '{db_image.path}'")
            return db_image
            
        except Exception as e:
            db.rollback()
            # Hapus file baru jika DB update gagal
            if os.path.exists(new_file_path):
                try:
                    os.remove(new_file_path)
                except Exception as e_rm:
                    logger.error(f"Failed to clean up new image {new_file_path} after DB error: {e_rm}")
            logger.error(f"DB error for updating medical image {unique_filename}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update medical image metadata in database.")

    def delete_medical_image(self, db: Session, image_id: int) -> Optional[MedicalImageModel]:
        db_image = self.get_medical_image(db=db, image_id=image_id)
        if db_image:
            # Optional: Hapus file fisik dari server
            # if os.path.exists(db_image.path):
            #     try:
            #         os.remove(db_image.path)
            #         logger.info(f"Successfully deleted image file: {db_image.path}")
            #     except OSError as e:
            #         logger.error(f"Error deleting file {db_image.path}: {e}")
            db.delete(db_image)
            db.commit()
        return db_image

medical_image_service = MedicalImageService()