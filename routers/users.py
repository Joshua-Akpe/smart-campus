from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import User, Complaint, Notification
from auth import hash_password, authenticate_user, create_access_token, get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")

#Register 
@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


@router.post("/register")
def register(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    matric_number: str = Form(None),
    password: str = Form(...),
    role: str = Form("student"),
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return templates.TemplateResponse(request=request, name="register.html", context={
            "request": request,
            "error": "An account with this email already exists."
        })
    if role not in ["student", "staff"]:
        role = "student"

    new_user = User(
        full_name=full_name,
        email=email,
        matric_number=matric_number or None,
        password_hash=hash_password(password),
        role=role
    )
    db.add(new_user)
    db.commit()

    return RedirectResponse(url="/login?registered=true", status_code=status.HTTP_302_FOUND)

#Login
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(request=request, name="login.html", context={
            "error": "Invalid email or password."
        })

    token = create_access_token(data={"sub": user.email})
    redirect_url = "/admin/dashboard" if user.role == "admin" else "/dashboard"
    response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response

#Logout
@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response

#Student dashboard
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    complaints = db.query(Complaint).filter(
        Complaint.user_id == current_user.id
    ).order_by(Complaint.created_at.desc()).all()

    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).all()

    return templates.TemplateResponse(
    request=request,
    name="dashboard.html",
    context={
        "user": current_user,
        "complaints": complaints,
        "notifications": notifications,
        "unread_count": len(notifications)
    }
)