from pydantic import BaseModel
from typing import Optional
class ChatRequest(BaseModel):
    user_id:str
    thread_id:Optional[str] = None
    message:str
    
class ChatResponse(BaseModel):
    thread_id:str
    response: str
    
        
class ThreadResponse(BaseModel):
    thread_id: str
    title: str