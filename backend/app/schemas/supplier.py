"""
Supplier schemas.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class SupplierBase(BaseModel):
    """Base supplier schema."""
    name: str
    tax_id: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None


class SupplierCreate(SupplierBase):
    """Supplier creation schema."""
    pass


class SupplierUpdate(BaseModel):
    """Supplier update schema."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class SupplierResponse(SupplierBase):
    """Supplier response schema."""
    id: int
    is_active: bool
    is_verified: bool
    risk_score: int

    class Config:
        from_attributes = True
