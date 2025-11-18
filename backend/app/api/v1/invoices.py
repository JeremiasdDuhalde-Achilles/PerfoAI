"""
Invoice API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import os
from datetime import datetime, timedelta

from app.core.security import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User
from app.models.invoice import Invoice
from app.models.supplier import Supplier
from app.schemas.invoice import (
    InvoiceResponse,
    InvoiceUpdate,
    InvoiceStats,
    DashboardMetrics
)
from app.agents.invoice_processor import invoice_processor
from app.core.config import settings

router = APIRouter()


@router.post("/upload", response_model=InvoiceResponse)
async def upload_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and process an invoice document.
    """
    # Validate file type
    allowed_extensions = [".pdf", ".xml", ".png", ".jpg", ".jpeg"]
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed: {allowed_extensions}"
        )

    # Save file
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, f"{datetime.now().timestamp()}_{file.filename}")

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Process invoice using AI agents
    processing_result = invoice_processor.process_invoice(
        document_path=file_path,
        document_format=file_ext[1:]  # Remove leading dot
    )

    # Find or create supplier
    supplier = db.query(Supplier).filter(
        Supplier.tax_id == processing_result.get("supplier_tax_id")
    ).first()

    if not supplier:
        supplier = Supplier(
            name=processing_result.get("supplier_name", "Unknown"),
            tax_id=processing_result.get("supplier_tax_id", f"TEMP-{datetime.now().timestamp()}"),
            is_active=True,
            is_verified=False
        )
        db.add(supplier)
        db.commit()
        db.refresh(supplier)

    # Create invoice record
    invoice = Invoice(
        invoice_number=processing_result.get("invoice_number", f"INV-{datetime.now().timestamp()}"),
        supplier_id=supplier.id,
        invoice_date=processing_result.get("invoice_date", datetime.now()),
        due_date=processing_result.get("due_date", datetime.now() + timedelta(days=30)),
        total_amount=processing_result.get("total_amount", 0),
        tax_amount=processing_result.get("tax_amount", 0),
        net_amount=processing_result.get("net_amount", 0),
        currency=processing_result.get("currency", "USD"),
        po_number=processing_result.get("po_number"),
        po_matched=processing_result.get("po_matched", False),
        status="pending" if processing_result.get("requires_approval") else "approved",
        processing_status=processing_result.get("processing_status", "completed"),
        confidence_score=processing_result.get("confidence_score", 0.0),
        is_touchless=processing_result.get("is_touchless", False),
        extracted_data=processing_result,
        validation_errors=processing_result.get("validation_errors"),
        gl_account=processing_result.get("gl_account"),
        cost_center=processing_result.get("cost_center"),
        document_path=file_path,
        document_format=file_ext[1:],
        approval_status="pending" if processing_result.get("requires_approval") else "approved",
        approved_by=None if processing_result.get("requires_approval") else current_user.id,
        approved_at=None if processing_result.get("requires_approval") else datetime.now(),
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return invoice


@router.get("/", response_model=List[InvoiceResponse])
def list_invoices(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all invoices with optional filtering.
    """
    query = db.query(Invoice)

    if status:
        query = query.filter(Invoice.status == status)

    invoices = query.offset(skip).limit(limit).all()
    return invoices


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get invoice by ID.
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    return invoice


@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "finance_manager", "approver"]))
):
    """
    Update invoice.
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    # Update fields
    for field, value in invoice_data.dict(exclude_unset=True).items():
        setattr(invoice, field, value)

    db.commit()
    db.refresh(invoice)

    return invoice


@router.post("/{invoice_id}/approve", response_model=InvoiceResponse)
def approve_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "finance_manager", "approver"]))
):
    """
    Approve an invoice.
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    invoice.approval_status = "approved"
    invoice.status = "approved"
    invoice.approved_by = current_user.id
    invoice.approved_at = datetime.now()

    db.commit()
    db.refresh(invoice)

    return invoice


@router.post("/{invoice_id}/reject", response_model=InvoiceResponse)
def reject_invoice(
    invoice_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "finance_manager", "approver"]))
):
    """
    Reject an invoice.
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    invoice.approval_status = "rejected"
    invoice.status = "rejected"
    invoice.rejection_reason = reason
    invoice.approved_by = current_user.id
    invoice.approved_at = datetime.now()

    db.commit()
    db.refresh(invoice)

    return invoice


@router.get("/stats/overview", response_model=InvoiceStats)
def get_invoice_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get invoice statistics.
    """
    total_invoices = db.query(func.count(Invoice.id)).scalar()
    pending_invoices = db.query(func.count(Invoice.id)).filter(Invoice.status == "pending").scalar()
    approved_invoices = db.query(func.count(Invoice.id)).filter(Invoice.status == "approved").scalar()
    rejected_invoices = db.query(func.count(Invoice.id)).filter(Invoice.status == "rejected").scalar()

    touchless_invoices = db.query(func.count(Invoice.id)).filter(Invoice.is_touchless == True).scalar()
    touchless_rate = (touchless_invoices / total_invoices * 100) if total_invoices > 0 else 0

    return {
        "total_invoices": total_invoices or 0,
        "pending_invoices": pending_invoices or 0,
        "approved_invoices": approved_invoices or 0,
        "rejected_invoices": rejected_invoices or 0,
        "touchless_rate": round(touchless_rate, 2),
        "avg_processing_time": 2.5  # Simulated
    }


@router.get("/dashboard/metrics", response_model=DashboardMetrics)
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard metrics for home page.
    """
    # Get invoices from last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)

    incoming_invoices = db.query(func.count(Invoice.id)).filter(
        Invoice.created_at >= thirty_days_ago
    ).scalar() or 0

    touchless_invoices = db.query(func.count(Invoice.id)).filter(
        and_(
            Invoice.is_touchless == True,
            Invoice.created_at >= thirty_days_ago
        )
    ).scalar() or 0

    touchless_rate = (touchless_invoices / incoming_invoices * 100) if incoming_invoices > 0 else 0

    pending_clarifications = db.query(func.count(Invoice.id)).filter(
        Invoice.processing_status == "pending_clarification"
    ).scalar() or 0

    # Calculate DPO (simplified)
    total_payables = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.status.in_(["pending", "approved"])
    ).scalar() or 0

    return {
        "incoming_invoices": incoming_invoices,
        "touchless_bookings": round(touchless_rate, 1),
        "days_payable_outstanding": 45.0,  # Simulated
        "realized_cash_discounts": 2.3,  # Simulated (in %)
        "invoice_cycle_time": 2.8,  # Simulated (in days)
        "pending_clarifications": pending_clarifications
    }
