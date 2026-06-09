from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VisitorCreate(BaseModel):
    session_id: str
    ip_address: Optional[str] = None
    country: Optional[str] = None
    source: Optional[str] = None

class PageVisitCreate(BaseModel):
    session_id: str
    page_url: str
    time_spent_seconds: float
    scroll_percentage: float

class ChatbotLogCreate(BaseModel):
    session_id: str
    question: str

class LeadCreate(BaseModel):
    session_id: str
    name: str
    email: str
    phone: str
    interest: Optional[str] = None

class AssessmentCreate(BaseModel):
    session_id: str
    email: str
    dob: Optional[str] = None
    qualification: Optional[str] = None
    gap: Optional[str] = None
    country: Optional[str] = None
    course: Optional[str] = None
    budget: Optional[str] = None
    income: Optional[str] = None

class NewsletterCreate(BaseModel):
    session_id: str
    email: str
