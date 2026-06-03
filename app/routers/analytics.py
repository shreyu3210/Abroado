from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.analytics import Visitor, PageVisit, ChatbotLog, Lead
from app.schemas.analytics import VisitorCreate, PageVisitCreate, ChatbotLogCreate, LeadCreate

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.post("/visitor")
async def create_visitor(visitor: VisitorCreate, request: Request, db: Session = Depends(get_db)):
    ip_address = visitor.ip_address or request.client.host
    
    existing = db.query(Visitor).filter(Visitor.session_id == visitor.session_id).first()
    if existing:
        return {"status": "already_exists", "session_id": existing.session_id}
        
    new_visitor = Visitor(
        session_id=visitor.session_id,
        ip_address=ip_address,
        country=visitor.country,
        source=visitor.source
    )
    db.add(new_visitor)
    db.commit()
    return {"status": "success"}

@router.post("/page_visit")
async def create_page_visit(page_visit: PageVisitCreate, db: Session = Depends(get_db)):
    new_visit = PageVisit(
        session_id=page_visit.session_id,
        page_url=page_visit.page_url,
        time_spent_seconds=page_visit.time_spent_seconds,
        scroll_percentage=page_visit.scroll_percentage
    )
    db.add(new_visit)
    db.commit()
    return {"status": "success"}

@router.post("/chatbot_log")
async def create_chatbot_log(log: ChatbotLogCreate, db: Session = Depends(get_db)):
    new_log = ChatbotLog(
        session_id=log.session_id,
        question=log.question
    )
    db.add(new_log)
    db.commit()
    return {"status": "success"}

@router.post("/lead")
async def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    new_lead = Lead(
        session_id=lead.session_id,
        name=lead.name,
        phone=lead.phone,
        interest=lead.interest
    )
    db.add(new_lead)
    db.commit()
    return {"status": "success"}
