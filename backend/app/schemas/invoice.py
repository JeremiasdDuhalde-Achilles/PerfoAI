"""
Invoice schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class InvoiceBase(BaseModel):
    """Base invoice schema."""
    invoice_number: str
    supplier_id: int
    invoice_date: datetime
    due_date: datetime
    total_amount: float
    tax_amount: float
    net_amount: float
    currency: str = "USD"
    po_number: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    """Invoice creation schema."""
    pass


class InvoiceUpdate(BaseModel):
    """Invoice update schema."""
    status: Optional[str] = None
    processing_status: Optional[str] = None
    gl_account: Optional[str] = None
    cost_center: Optional[str] = None
    notes: Optional[str] = None


class InvoiceResponse(InvoiceBase):
    """Invoice response schema."""
    id: int
    status: str
    processing_status: str
    confidence_score: float
    is_touchless: bool
    po_matched: bool
    approval_status: str
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceStats(BaseModel):
    """Invoice statistics."""
    total_invoices: int
    pending_invoices: int
    approved_invoices: int
    rejected_invoices: int
    touchless_rate: float
    avg_processing_time: float


class DashboardMetrics(BaseModel):
    """Dashboard metrics."""
    incoming_invoices: int
    touchless_bookings: float
    days_payable_outstanding: float
    realized_cash_discounts: float
    invoice_cycle_time: float
    pending_clarifications: int
