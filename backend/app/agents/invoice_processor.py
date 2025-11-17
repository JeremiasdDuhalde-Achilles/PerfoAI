"""
Invoice Processor - Main orchestrator using LangGraph.
"""
from typing import Dict, Any
from datetime import datetime
import time

from langgraph.graph import StateGraph, END
from app.agents.state import InvoiceProcessingState
from app.agents.ocr_agent import OCRAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.coding_agent import CodingAgent
from app.agents.approval_agent import ApprovalAgent


class InvoiceProcessor:
    """
    Main invoice processor using LangGraph for workflow orchestration.

    Workflow:
    1. OCR: Extract data from document
    2. Validation: Validate extracted data
    3. Coding: Assign GL accounts
    4. Approval: Determine approval requirements
    5. ERP: Post to ERP (if touchless) or send for approval
    """

    def __init__(self):
        """Initialize processor with all agents."""
        self.ocr_agent = OCRAgent()
        self.validation_agent = ValidationAgent()
        self.coding_agent = CodingAgent()
        self.approval_agent = ApprovalAgent()

        # Build workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the invoice processing workflow using LangGraph."""

        # Create workflow graph
        workflow = StateGraph(InvoiceProcessingState)

        # Add nodes (agents)
        workflow.add_node("ocr", self.ocr_agent.process)
        workflow.add_node("validation", self.validation_agent.process)
        workflow.add_node("coding", self.coding_agent.process)
        workflow.add_node("approval", self.approval_agent.process)
        workflow.add_node("finalize", self._finalize)

        # Define edges (workflow flow)
        workflow.set_entry_point("ocr")

        # OCR -> Validation
        workflow.add_edge("ocr", "validation")

        # Validation -> Coding or Clarification
        workflow.add_conditional_edges(
            "validation",
            self._should_continue_after_validation,
            {
                "continue": "coding",
                "clarification": "finalize",
                "reject": "finalize"
            }
        )

        # Coding -> Approval
        workflow.add_edge("coding", "approval")

        # Approval -> Finalize
        workflow.add_edge("approval", "finalize")

        # Finalize -> End
        workflow.add_edge("finalize", END)

        return workflow.compile()

    def _should_continue_after_validation(self, state: InvoiceProcessingState) -> str:
        """
        Decide next step after validation.

        Returns:
            "continue" - proceed to coding
            "clarification" - needs manual review
            "reject" - reject invoice
        """
        if state.get("fraud_detected", False):
            return "reject"

        if state.get("clarification_needed", False):
            return "clarification"

        if state.get("is_valid", True):
            return "continue"

        # Has errors but not critical
        if len(state.get("validation_errors", [])) > 3:
            return "clarification"

        return "continue"

    def _finalize(self, state: InvoiceProcessingState) -> InvoiceProcessingState:
        """
        Finalize processing and determine final status.

        Args:
            state: Current processing state

        Returns:
            Final state with processing results
        """
        # Calculate processing time
        state["processed_at"] = datetime.utcnow()

        # Determine final status
        if state.get("fraud_detected", False):
            final_status = "rejected"
            processing_status = "rejected_fraud"

        elif state.get("clarification_needed", False):
            final_status = "pending"
            processing_status = "pending_clarification"

        elif state.get("requires_approval", False):
            final_status = "pending"
            processing_status = "pending_approval"

        elif state.get("is_touchless", False):
            final_status = "approved"
            processing_status = "completed"

        else:
            final_status = "pending"
            processing_status = "pending_review"

        # Update state with final status
        state["current_step"] = "completed"

        return state

    def process_invoice(self, document_path: str, document_format: str) -> Dict[str, Any]:
        """
        Process an invoice through the complete workflow.

        Args:
            document_path: Path to invoice document
            document_format: Format of document (pdf, xml, etc.)

        Returns:
            Processing results
        """
        start_time = time.time()

        # Initialize state
        initial_state: InvoiceProcessingState = {
            "document_path": document_path,
            "document_format": document_format,
            "document_content": None,
            "invoice_number": None,
            "supplier_name": None,
            "supplier_tax_id": None,
            "invoice_date": None,
            "due_date": None,
            "total_amount": None,
            "tax_amount": None,
            "net_amount": None,
            "currency": None,
            "po_number": None,
            "line_items": None,
            "validation_errors": [],
            "confidence_score": 0.0,
            "is_valid": True,
            "fraud_detected": False,
            "duplicate_detected": False,
            "po_matched": False,
            "po_data": None,
            "supplier_id": None,
            "gl_account": None,
            "cost_center": None,
            "accounting_entries": None,
            "requires_approval": False,
            "approval_threshold": 0.0,
            "approver_id": None,
            "current_step": "initialized",
            "is_touchless": False,
            "processing_errors": [],
            "clarification_needed": False,
            "clarification_message": None,
            "processed_at": None,
            "processing_time": None,
        }

        # Run workflow
        final_state = self.workflow.invoke(initial_state)

        # Calculate processing time
        processing_time = time.time() - start_time
        final_state["processing_time"] = processing_time

        return final_state


# Global processor instance
invoice_processor = InvoiceProcessor()
