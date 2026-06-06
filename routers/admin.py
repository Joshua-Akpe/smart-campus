from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Complaint, StatusUpdate, Notification, User, ComplaintStatus, ComplaintCategory
from auth import get_current_admin

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")


#Admin Dashboard
@router.get("/dashboard", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
    status_filter: str = None,
    category_filter: str = None
):
    query = db.query(Complaint)

    if status_filter:
        query = query.filter(Complaint.status == status_filter)
    if category_filter:
        query = query.filter(Complaint.category == category_filter)

    complaints = query.order_by(Complaint.created_at.desc()).all()

    # Analytics counts
    total = db.query(func.count(Complaint.id)).scalar()
    pending = db.query(func.count(Complaint.id)).filter(Complaint.status == "pending").scalar()
    in_progress = db.query(func.count(Complaint.id)).filter(Complaint.status == "in_progress").scalar()
    resolved = db.query(func.count(Complaint.id)).filter(Complaint.status == "resolved").scalar()

    # Category breakdown for chart
    category_data = db.query(
        Complaint.category, func.count(Complaint.id)
    ).group_by(Complaint.category).all()

    return templates.TemplateResponse(
    request=request,
    name="admin_dashboard.html",
    context={
        "user": current_user,
        "complaints": complaints,
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "resolved": resolved,
        "category_data": {cat: count for cat, count in category_data},
        "statuses": [s.value for s in ComplaintStatus],
        "categories": [c.value for c in ComplaintCategory],
        "status_filter": status_filter,
        "category_filter": category_filter
    }
)


#Update Complaint Status
@router.post("/complaints/{complaint_id}/update")
def update_complaint_status(
    complaint_id: int,
    new_status: str = Form(...),
    note: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)

    old_status = complaint.status

    status_update = StatusUpdate(
        complaint_id=complaint_id,
        updated_by=current_user.id,
        old_status=old_status,
        new_status=new_status,
        note=note
    )
    db.add(status_update)

    complaint.status = new_status

    notification = Notification(
        user_id=complaint.user_id,
        message=f"Your complaint '{complaint.title}' status has been updated to: "
                f"{new_status.replace('_', ' ').title()}."
                + (f" Note: {note}" if note else "")
    )
    db.add(notification)
    db.commit()

    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)


#View Single Complaint (Admin)
@router.get("/complaints/{complaint_id}", response_class=HTMLResponse)
def admin_view_complaint(
    complaint_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("my_complaints.html", {
        "request": request,
        "user": current_user,
        "complaint": complaint,
        "status_updates": complaint.status_updates,
        "statuses": [s.value for s in ComplaintStatus],
        "is_admin": True
    })