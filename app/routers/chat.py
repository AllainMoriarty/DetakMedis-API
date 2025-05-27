from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import rag_service
from app.core.database import get_db

router = APIRouter(prefix="/chat", tags=["Chatbot"])

@router.post("/", response_model=ChatResponse)
async def handle_chat(request: ChatRequest, db: Session = Depends(get_db)):
    if not request.query:
        raise HTTPException(status_code=400, detail="Query tidak boleh kosong.")
    
    try:
        response = await rag_service.process_chat(db, request)
        return response
    except Exception as e:
        # Log the exception
        print(f"Error during chat processing: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")