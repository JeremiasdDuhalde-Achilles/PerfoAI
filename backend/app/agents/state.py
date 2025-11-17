"""
Agent state definitions for LangGraph.
"""
from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime


class InvoiceProcessingState(TypedDict):
    """State for invoice processing workflow."""

    # Document information
    document_path: str
    document_format: str
    document_content: Optional[bytes]

    # Extracted data
    invoice_number: Optional[str]
    supplier_name: Optional[str]
    supplier_tax_id: Optional[str]
    invoice_date: Optional[datetime]
    due_date: Optional[datetime]
    total_amount: Optional[float]
    tax_amount: Optional[float]
    net_amount: Optional[float]
    currency: Optional[str]
    po_number: Optional[str]
    line_items: Optional[List[Dict[str, Any]]]

    # Validation results
    validation_errors: List[str]
    confidence_score: float
    is_valid: bool
    fraud_detected: bool
    duplicate_detected: bool

    # Matching results
    po_matched: bool
    po_data: Optional[Dict[str, Any]]
    supplier_id: Optional[int]

    # Accounting coding
    gl_account: Optional[str]
    cost_center: Optional[str]
    accounting_entries: Optional[List[Dict[str, Any]]]

    # Approval workflow
    requires_approval: bool
    approval_threshold: float
    approver_id: Optional[int]

    # Processing status
    current_step: str
    is_touchless: bool
    processing_errors: List[str]
    clarification_needed: bool
    clarification_message: Optional[str]

    # Metadata
    processed_at: Optional[datetime]
    processing_time: Optional[float]
