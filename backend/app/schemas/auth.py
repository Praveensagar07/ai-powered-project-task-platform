"""Authentication Pydantic schemas."""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.schemas.user import UserResponse


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="User full name")
    email: EmailStr = Field(..., description="User unique email")
    password: str = Field(..., min_length=6, max_length=100, description="Password (min 6 chars)")
    role: Optional[str] = Field("Full Stack Developer", max_length=50)


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Registered email")
    password: str = Field(..., min_length=1, description="Password")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthResponse(BaseModel):
    user: UserResponse
    token: TokenResponse
