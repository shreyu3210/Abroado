from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timedelta
from app.db.database import Base

def get_ist_time():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

class Visitor(Base):
    __tablename__ = "visitors"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    ip_address = Column(String, nullable=True)
    country = Column(String, nullable=True)
    source = Column(String, nullable=True)
    created_at = Column(DateTime, default=get_ist_time)

class PageVisit(Base):
    __tablename__ = "page_visits"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    page_url = Column(String, nullable=False)
    time_spent_seconds = Column(Float, default=0.0)
    scroll_percentage = Column(Float, default=0.0)
    created_at = Column(DateTime, default=get_ist_time)

class ChatbotLog(Base):
    __tablename__ = "chatbot_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    question = Column(String, nullable=False)
    created_at = Column(DateTime, default=get_ist_time)

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, default="")
    phone = Column(String, nullable=False)
    interest = Column(String, nullable=True)
    created_at = Column(DateTime, default=get_ist_time)

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    email = Column(String, nullable=False)
    dob = Column(String, nullable=True)
    qualification = Column(String, nullable=True)
    gap = Column(String, nullable=True)
    country = Column(String, nullable=True)
    course = Column(String, nullable=True)
    budget = Column(String, nullable=True)
    income = Column(String, nullable=True)
    created_at = Column(DateTime, default=get_ist_time)
