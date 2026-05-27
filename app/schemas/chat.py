from pydantic import BaseModel
from typing import List, Any

class Message(BaseModel):
    role: str
    content: Any

class ChatRequest(BaseModel):
    messages: List[Message]
