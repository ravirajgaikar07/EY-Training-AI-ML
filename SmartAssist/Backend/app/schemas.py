from pydantic import BaseModel
from typing import List, Optional, Any

class UploadResponse(BaseModel):
    success: bool
    message: str
    files_processed: List[str]

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    conversation_history: List[dict]

class HumanRequest(BaseModel):
    reply: str
