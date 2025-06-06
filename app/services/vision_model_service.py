import onnxruntime  
from PIL import Image 
import numpy as np  
import io  
import logging  
from typing import Dict, Any, List, Optional 
import scipy.special  
from app.core.config import settings

# Logger untuk pencatatan informasi dan error
logger = logging.getLogger(__name__)

# Daftar penyakit yang sesuai dengan urutan output model
DISEASE_NAMES_FROM_MODEL_OUTPUT = [
    "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration", "Mass", "Nodule",
    "Pneumonia", "Pneumothorax", "Consolidation", "Edema", "Emphysema",
    "Fibrosis", "Pleural_Thickening", "Hernia"
] 

# Ukuran gambar input model
MODEL_IMAGE_SIZE = 224


class VisionModelService:
    """
    Kelas layanan untuk memproses gambar X-ray dan memprediksi kemungkinan penyakit menggunakan model ONNX.
    """

    def __init__(self, model_path: str = settings.ONNX_MODEL_PATH):
        """Inisialisasi layanan dengan path ke model."""
        self.model_path = model_path
        self.session = None  # Session inference ONNX
        self.input_name: Optional[str] = None  # Nama input model
        self.output_name: Optional[str] = None  # Nama output model
        self._load_model()  # Muat model saat inisialisasi

    def _load_model(self):
        """Memuat model ONNX ke dalam session inference."""
        try:
            self.session = onnxruntime.InferenceSession(self.model_path, providers=['CPUExecutionProvider'])
            if not self.session.get_inputs() or not self.session.get_outputs():
                logger.error("ONNX model inputs or outputs are empty.")
                self.session = None
                return
            self.input_name = self.session.get_inputs()[0].name
            self.output_name = self.session.get_outputs()[0].name
            logger.info(f"Vision model loaded: {self.model_path}, Input: {self.input_name}, Output: {self.output_name}")
            model_output_shape = self.session.get_outputs()[0].shape
            if len(model_output_shape) < 2 or model_output_shape[-1] != len(DISEASE_NAMES_FROM_MODEL_OUTPUT):
                logger.error(f"Model output shape mismatch: {model_output_shape[-1]} vs {len(DISEASE_NAMES_FROM_MODEL_OUTPUT)}")
        except Exception as e:
            logger.error(f"Failed to load ONNX model from {self.model_path}: {e}")
            self.session = None

    def _preprocess_image(self, image_data: bytes) -> Optional[np.ndarray]:
        """Praproses gambar dari bytes ke format tensor float32 yang siap dipakai model."""
        try:
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
            image = image.resize((MODEL_IMAGE_SIZE, MODEL_IMAGE_SIZE), Image.LANCZOS)
            image_np = np.array(image, dtype=np.float32)

            mean = np.array([0.485, 0.456, 0.406]) 
            std = np.array([0.229, 0.224, 0.225])  
            image_np = (image_np / 255.0 - mean) / std  # Normalisasi

            image_np = np.transpose(image_np, (2, 0, 1))  # Ubah format HWC ke CHW
            image_np = np.expand_dims(image_np, axis=0)  # Tambahkan batch dimension
            return image_np.astype(np.float32)
        except Exception as e:
            logger.error(f"Error during image preprocessing: {e}")
            return None

    def _postprocess_output(self, model_output_onnx: List[np.ndarray]) -> Dict[str, float]:
        """Postproses output model menjadi probabilitas kelas penyakit."""
        logits = model_output_onnx[0][0]  # Ambil logit dari batch pertama

        if len(logits) != len(DISEASE_NAMES_FROM_MODEL_OUTPUT):
            logger.error(f"Mismatch in output logits size: {len(logits)} vs {len(DISEASE_NAMES_FROM_MODEL_OUTPUT)}")
            return {}

        probabilities_raw = scipy.special.softmax(logits)  # Softmax untuk probabilitas
        predictions: Dict[str, float] = {}
        for i, disease_name in enumerate(DISEASE_NAMES_FROM_MODEL_OUTPUT):
            prob_percent = round(float(probabilities_raw[i]) * 100, 2)
            predictions[disease_name] = prob_percent
        return predictions

    async def predict_disease_probabilities(self, image_data: bytes) -> Dict[str, float]:
        """Metode utama untuk prediksi penyakit berdasarkan gambar."""
        if not self.session or not self.input_name:
            logger.error("Vision model session/input name not available.")
            return {}

        processed_input = self._preprocess_image(image_data)
        if processed_input is None:
            return {}

        try:
            model_output_onnx = self.session.run([self.output_name], {self.input_name: processed_input})
            return self._postprocess_output(model_output_onnx)
        except Exception as e:
            logger.error(f"Error during vision model inference: {e}")
            return {}

vision_model_service = VisionModelService()