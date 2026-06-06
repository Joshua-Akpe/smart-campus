from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from models import UserRole, ComplaintCategory, ComplaintStatus

#user schemas
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    matric_number: Optional[str] = None
    role: UserRole = UserRole.student

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    matric_number: Optional[str]
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True

#complaint schemas
class ComplaintCreate(BaseModel):
    title: str
    description: str
    category: ComplaintCategory


class ComplaintOut(BaseModel):
    id: int
    title: str
    description: str
    category: ComplaintCategory
    status: ComplaintStatus
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

#status update schemas
class ComplaintStatusUpdate(BaseModel):
    new_status: ComplaintStatus
    note: Optional[str] = None


class StatusUpdateOut(BaseModel):
    id: int
    complaint_id: int
    old_status: ComplaintStatus
    new_status: ComplaintStatus
    note: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True

#notification schemas
class NotificationOut(BaseModel):
    id: int
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

#auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None