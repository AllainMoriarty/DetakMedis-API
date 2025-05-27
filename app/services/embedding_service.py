from langchain_ollama import OllamaEmbeddings
from app.core.config import settings

class EmbeddingService:
    def __init__(self):
        self.embedding_model = OllamaEmbeddings(
            model=settings.EMBEDDING_MODEL_NAME,
            base_url=settings.OLLAMA_BASE_URL
        )
    
    async def get_embedding(self, text: str) -> list[float]:
        return await self.embedding_model.aembed_query(text)

embedding_service = EmbeddingService()