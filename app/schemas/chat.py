from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ChatRequest(BaseModel):
    query: str

class ContextDocument(BaseModel):
    source: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    answer: str
    retrieved_contexts: List[ContextDocument]