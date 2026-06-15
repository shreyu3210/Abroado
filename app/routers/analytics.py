from fastapi import APIRouter, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.analytics import Visitor, Lead, Assessment
from app.schemas.analytics import VisitorCreate, LeadCreate, AssessmentCreate, NewsletterCreate
from app.services.email_service import send_email, get_template
import os

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

def send_lead_emails_background(name, email, phone, interest):
    admin_email = os.getenv("EMAIL_USER")
    templates = get_template("contact_template")
    
    if templates:
        # Send to User
        user_body = templates.get("user_body", "").replace("{name}", name).replace("{interest}", interest or "our services")
        send_email(email, templates.get("user_subject", "Thank you!"), user_body)
        
        # Send to Admin (or info@abroado.info if configured)
        admin_body = templates.get("admin_body", "").replace("{name}", name).replace("{email}", email).replace("{phone}", phone).replace("{interest}", interest or "None")
        admin_subject = templates.get("admin_subject", "New Lead").replace("{name}", name)
        send_email(admin_email, admin_subject, admin_body)

def send_newsletter_email_background(email):
    admin_email = os.getenv("EMAIL_USER")
    templates = get_template("newsletter_template")
    
    if templates:
        user_body = templates.get("user_body", "")
        send_email(email, templates.get("user_subject", "Subscription Confirmed"), user_body)
        
        admin_body = templates.get("admin_body", "").replace("{email}", email)
        send_email(admin_email, templates.get("admin_subject", "New Subscriber"), admin_body)

def send_assessment_email_background(assessment):
    admin_email = "info@abroado.in"  # explicitly target this email for notifications
    templates = get_template("assessment_template")
    
    if templates:
        admin_body = templates.get("admin_body", "")
        admin_body = admin_body.replace("{name}", assessment.name or "N/A")
        admin_body = admin_body.replace("{surname}", assessment.surname or "N/A")
        admin_body = admin_body.replace("{email}", assessment.email or "N/A")
        admin_body = admin_body.replace("{dob}", assessment.dob or "N/A")
        admin_body = admin_body.replace("{qualification}", assessment.qualification or "N/A")
        admin_body = admin_body.replace("{gap}", assessment.gap or "N/A")
        admin_body = admin_body.replace("{country}", assessment.country or "N/A")
        admin_body = admin_body.replace("{course}", assessment.course or "N/A")
        admin_body = admin_body.replace("{budget}", assessment.budget or "N/A")
        admin_body = admin_body.replace("{income}", assessment.income or "N/A")
        
        send_email(admin_email, templates.get("admin_subject", "New Profile Assessment"), admin_body)

# ... (other endpoints omitted for this replacement block) ...

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

# @router.post("/page_visit")
# async def create_page_visit(page_visit: PageVisitCreate, db: Session = Depends(get_db)):
#     new_visit = PageVisit(
#         session_id=page_visit.session_id,
#         page_url=page_visit.page_url,
#         time_spent_seconds=page_visit.time_spent_seconds,
#         scroll_percentage=page_visit.scroll_percentage
#     )
#     db.add(new_visit)
#     db.commit()
#     return {"status": "success"}

# @router.post("/chatbot_log")
# async def create_chatbot_log(log: ChatbotLogCreate, db: Session = Depends(get_db)):
#     new_log = ChatbotLog(
#         session_id=log.session_id,
#         question=log.question
#     )
#     db.add(new_log)
#     db.commit()
#     return {"status": "success"}

@router.post("/lead")
async def create_lead(lead: LeadCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    new_lead = Lead(
        session_id=lead.session_id,
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        interest=lead.interest
    )
    db.add(new_lead)
    db.commit()
    
    # Send email asynchronously
    background_tasks.add_task(send_lead_emails_background, lead.name, lead.email, lead.phone, lead.interest)
    
    return {"status": "success"}

@router.post("/newsletter")
async def subscribe_newsletter(newsletter: NewsletterCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # You can also save this to a Newsletter subscriber table if needed later
    background_tasks.add_task(send_newsletter_email_background, newsletter.email)
    return {"status": "success"}

@router.post("/assessment")
async def create_assessment(assessment: AssessmentCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    new_assessment = Assessment(
        session_id=assessment.session_id,
        name=assessment.name,
        surname=assessment.surname,
        email=assessment.email,
        dob=assessment.dob,
        qualification=assessment.qualification,
        gap=assessment.gap,
        country=assessment.country,
        course=assessment.course,
        budget=assessment.budget,
        income=assessment.income
    )
    db.add(new_assessment)
    db.commit()
    
    # Send notification email asynchronously
    background_tasks.add_task(send_assessment_email_background, assessment)
    
    return {"status": "success"}
