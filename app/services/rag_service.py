from sqlalchemy.orm import Session
from app.services.embedding_service import embedding_service
from app.services.llm_service import llm_service
from app.services.retrieval_service import retrieval_service
from app.schemas.chat import ChatRequest, ChatResponse, ContextDocument
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGService:
    async def process_chat(self, db: Session, chat_request: ChatRequest) -> ChatResponse:
        logger.info(f"--- RAGService.process_chat START ---")
        logger.info(f"Query: {chat_request.query}")

        # 1. Get query embedding
        logger.info("Step 1: Calling embedding_service.get_embedding...")
        try:
            # Periksa apa yang dikembalikan SEBELUM await jika get_embedding bukan async (tapi ia async)
            # embedding_coroutine = embedding_service.get_embedding(chat_request.query)
            # logger.info(f"Type of embedding_coroutine: {type(embedding_coroutine)}")
            query_embedding = await embedding_service.get_embedding(chat_request.query)
            logger.info(f"Type of query_embedding AFTER await: {type(query_embedding)}")
            if isinstance(query_embedding, str):
                logger.error("!!! ERROR: embedding_service.get_embedding returned a str AFTER await!")
                raise TypeError("embedding_service.get_embedding returned str") # Hentikan di sini jika error
        except Exception as e:
            logger.exception("Exception during embedding_service.get_embedding")
            raise

        # 2. Retrieve relevant documents
        logger.info("Step 2: Calling retrieval_service.retrieve_documents...")
        try:
            # retrieval_coroutine = retrieval_service.retrieve_documents(db, query_embedding)
            # logger.info(f"Type of retrieval_coroutine: {type(retrieval_coroutine)}")
            retrieved_docs = await retrieval_service.retrieve_documents(db, query_embedding)
            logger.info(f"Type of retrieved_docs AFTER await: {type(retrieved_docs)}")
            if isinstance(retrieved_docs, str):
                logger.error("!!! ERROR: retrieval_service.retrieve_documents returned a str AFTER await!")
                raise TypeError("retrieval_service.retrieve_documents returned str")
        except Exception as e:
            logger.exception("Exception during retrieval_service.retrieve_documents")
            raise

        # 3. Format context for LLM
        logger.info("Step 3: Formatting context...")
        context_str = "\n\n".join([f"Sumber: {doc.source}\nKonten: {doc.content}" for doc in retrieved_docs])
        if not retrieved_docs:
            context_str = "Tidak ada informasi relevan yang ditemukan di database."
        logger.info(f"Context string (first 100 chars): {context_str[:100]}")

        # 4. Generate response using LLM
        logger.info("Step 4: Calling llm_service.generate_response...")
        try:
            # llm_coroutine = llm_service.generate_response(question=chat_request.query, context=context_str)
            # logger.info(f"Type of llm_coroutine: {type(llm_coroutine)}")
            answer = await llm_service.generate_response(question=chat_request.query, context=context_str)
            logger.info(f"Type of answer AFTER await: {type(answer)}")
            if not isinstance(answer, str): # Di sini kita MENGHARAPKAN string
                logger.warning(f"LLM response (answer) is not a string, it's: {type(answer)}")
                # Ini bukan error "await str", tapi mungkin menunjukkan masalah lain.
                # Namun, jika 'answer' di sini adalah string, dan error 'await str' terjadi,
                # maka error itu pasti terjadi DI DALAM llm_service.generate_response.
        except Exception as e:
            # Jika error "await str" terjadi DI DALAM llm_service.generate_response,
            # exception akan tertangkap di sini.
            logger.exception("Exception during llm_service.generate_response")
            raise

        logger.info(f" {answer}")
        logger.info(f"--- RAGService.process_chat END ---")
        return ChatResponse(answer=str(answer), retrieved_contexts=retrieved_docs) # Pastikan answer adalah str

rag_service = RAGService()