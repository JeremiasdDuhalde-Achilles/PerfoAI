"""
Authentication schemas.
"""
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Token response."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data."""
    user_id: int | None = None


class LoginRequest(BaseModel):
    """Login request."""
    username: str
    password: str


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str
    full_name: str
    role: str


class UserCreate(UserBase):
    """User creation schema."""
    password: str


class UserUpdate(BaseModel):
    """User update schema."""
    email: EmailStr | None = None
    full_name: str | None = None
    role: str | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    """User response schema."""
    id: int
    is_active: bool

    class Config:
        from_attributes = True
