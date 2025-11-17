"""
Supplier model for managing vendors.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Supplier(Base):
    """Supplier/Vendor model."""

    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    tax_id = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    country = Column(String, nullable=True)

    # Payment terms
    default_payment_terms = Column(String, nullable=True)
    default_early_payment_discount = Column(String, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Risk assessment
    risk_score = Column(Integer, default=0)  # 0-100

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    invoices = relationship("Invoice", back_populates="supplier")

    def __repr__(self):
        return f"<Supplier(name='{self.name}', tax_id='{self.tax_id}')>"
