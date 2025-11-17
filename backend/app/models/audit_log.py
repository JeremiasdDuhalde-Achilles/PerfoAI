"""
Audit log model for tracking all system activities.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from app.db.session import Base


class AuditLog(Base):
    """Audit log for tracking user and system activities."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)  # create, update, delete, approve, reject, etc.
    entity_type = Column(String, nullable=False)  # invoice, supplier, user, etc.
    entity_id = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    changes = Column(JSON, nullable=True)  # Store what changed
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<AuditLog(action='{self.action}', entity='{self.entity_type}:{self.entity_id}')>"
