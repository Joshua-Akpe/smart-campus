from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import Complaint, Notification, ComplaintCategory
from auth import get_current_user
from models import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")

#Submit Complaint Page
@router.get("/complaints/submit", response_class=HTMLResponse)
def submit_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    return templates.TemplateResponse(
        request=request,
        name="submit_complaint.html",
        context={
            "user": current_user,
            "categories": [c.value for c in ComplaintCategory]
        }
    )


@router.post("/complaints/submit")
def submit_complaint(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    complaint = Complaint(
        title=title,
        description=description,
        category=category,
        user_id=current_user.id
    )
    db.add(complaint)
    db.flush()

    notification = Notification(
        user_id=current_user.id,
        message=f"Your complaint '{title}' has been submitted and is pending review."
    )
    db.add(notification)
    db.commit()

    return RedirectResponse(url="/dashboard?submitted=true", status_code=status.HTTP_302_FOUND)

#View Single Complaint
@router.get("/complaints/{complaint_id}", response_class=HTMLResponse)
def view_complaint(
    complaint_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()

    if not complaint:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    if current_user.role != "admin" and complaint.user_id != current_user.id:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        request=request,
        name="my_complaints.html",
        context={
            "user": current_user,
            "complaint": complaint,
            "status_updates": complaint.status_updates
        }
    )

#Mark Notifications as Read
@router.post("/notifications/read")
def mark_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()

    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)