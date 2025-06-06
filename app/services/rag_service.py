from sqlalchemy.orm import Session  
from app.services.embedding_service import embedding_service  
from app.services.llm_service import llm_service  
from app.services.retrieval_service import retrieval_service  
from app.schemas.chat import ChatRequest, ChatResponse, ContextDocument  
from typing import List  
import logging  

# Konfigurasi dasar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) 

class RAGService:
    """
    Kelas utama yang mengelola proses chat menggunakan pendekatan Retrieval-Augmented Generation (RAG).
    """

    async def process_chat(self, db: Session, chat_request: ChatRequest) -> ChatResponse:
        """
        Memproses permintaan chat dari pengguna dengan alur:
        1. Menghasilkan embedding dari query
        2. Mencari dokumen relevan
        3. Menyusun konteks dari dokumen
        4. Menghasilkan jawaban dengan LLM
        
        Args:
            db (Session): Sesi database SQLAlchemy.
            chat_request (ChatRequest): Permintaan chat dari pengguna.

        Returns:
            ChatResponse: Jawaban dari sistem beserta konteks dokumen yang digunakan.
        """
        logger.info(f"--- RAGService.process_chat START ---")
        logger.info(f"Query: {chat_request.query}")

        # 1. Menghasilkan embedding dari query pengguna
        logger.info("Step 1: Calling embedding_service.get_embedding...")
        try:
            query_embedding = await embedding_service.get_embedding(chat_request.query)
            logger.info(f"Type of query_embedding AFTER await: {type(query_embedding)}")
            if isinstance(query_embedding, str):
                logger.error("!!! ERROR: embedding_service.get_embedding returned a str AFTER await!")
                raise TypeError("embedding_service.get_embedding returned str")
        except Exception as e:
            logger.exception("Exception during embedding_service.get_embedding")
            raise

        # 2. Mencari dokumen yang relevan berdasarkan embedding
        logger.info("Step 2: Calling retrieval_service.retrieve_documents...")
        try:
            retrieved_docs = await retrieval_service.retrieve_documents(db, query_embedding)
            logger.info(f"Type of retrieved_docs AFTER await: {type(retrieved_docs)}")
            if isinstance(retrieved_docs, str):
                logger.error("!!! ERROR: retrieval_service.retrieve_documents returned a str AFTER await!")
                raise TypeError("retrieval_service.retrieve_documents returned str")
        except Exception as e:
            logger.exception("Exception during retrieval_service.retrieve_documents")
            raise

        # 3. Menyusun konteks dari dokumen yang ditemukan
        logger.info("Step 3: Formatting context...")
        context_str = "\n\n".join([f"Sumber: {doc.source}\nKonten: {doc.content}" for doc in retrieved_docs])
        if not retrieved_docs:
            context_str = "Tidak ada informasi relevan yang ditemukan di database."
        logger.info(f"Context string (first 100 chars): {context_str[:100]}")

        # 4. Menghasilkan jawaban menggunakan layanan LLM
        logger.info("Step 4: Calling llm_service.generate_response...")
        try:
            answer = await llm_service.generate_response(question=chat_request.query, context=context_str)
            logger.info(f"Type of answer AFTER await: {type(answer)}")
            if not isinstance(answer, str):
                logger.warning(f"LLM response (answer) is not a string, it's: {type(answer)}")
        except Exception as e:
            logger.exception("Exception during llm_service.generate_response")
            raise

        logger.info(f"{answer}")
        logger.info(f"--- RAGService.process_chat END ---")

        # Mengembalikan respons chat sebagai objek ChatResponse
        return ChatResponse(answer=str(answer), retrieved_contexts=retrieved_docs)

rag_service = RAGService()