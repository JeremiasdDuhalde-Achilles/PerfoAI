"""
Invoice model for managing invoices.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Invoice(Base):
    """Invoice model."""

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, index=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)

    # Invoice details
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    total_amount = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=False)
    net_amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")

    # Purchase Order
    po_number = Column(String, nullable=True)
    po_matched = Column(Boolean, default=False)

    # Status tracking
    status = Column(String, nullable=False)  # pending, validated, approved, rejected, posted, paid
    processing_status = Column(String, default="inbox")  # inbox, processing, clarification, completed

    # AI Processing
    confidence_score = Column(Float, default=0.0)
    is_touchless = Column(Boolean, default=False)
    extracted_data = Column(JSON, nullable=True)
    validation_errors = Column(JSON, nullable=True)

    # Payment
    payment_terms = Column(String, nullable=True)
    early_payment_discount = Column(Float, default=0.0)
    discount_due_date = Column(DateTime, nullable=True)
    payment_date = Column(DateTime, nullable=True)

    # Accounting
    gl_account = Column(String, nullable=True)
    cost_center = Column(String, nullable=True)

    # Document reference
    document_path = Column(String, nullable=True)
    document_format = Column(String, nullable=True)  # pdf, xml, etc.

    # Approval workflow
    approval_status = Column(String, default="pending")  # pending, in_review, approved, rejected
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Notes and comments
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    supplier = relationship("Supplier", back_populates="invoices")
    approver = relationship("User", foreign_keys=[approved_by])

    def __repr__(self):
        return f"<Invoice(number='{self.invoice_number}', supplier_id={self.supplier_id}, status='{self.status}')>"
