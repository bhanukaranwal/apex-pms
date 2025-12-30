from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from backend.core.models import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    role: Optional[UserRole] = UserRole.ANALYST

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str
    exp: int
    type: str
