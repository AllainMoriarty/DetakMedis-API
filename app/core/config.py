from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/dbname")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "nomic-embed-text:latest")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME")
    EMBEDDING_DIM: int = 768 # Sesuai dengan Vector(768) pada model Anda
    ONNX_MODEL_PATH: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../scripts/vit_adapter_model.onnx"))

    # Retrieval settings
    SIMILARITY_TOP_K: int = 5

    UPLOAD_IMAGE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../images/"))

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()