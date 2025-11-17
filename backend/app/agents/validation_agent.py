"""
Validation Agent for verifying invoice data.
"""
from typing import List
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate

from app.core.config import settings
from app.agents.state import InvoiceProcessingState


class ValidationAgent:
    """Agent responsible for validating invoice data."""

    def __init__(self):
        """Initialize validation agent."""
        self.llm = AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            deployment_name=settings.AZURE_OPENAI_DEPLOYMENT,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            temperature=0,
        )

    def process(self, state: InvoiceProcessingState) -> InvoiceProcessingState:
        """
        Validate invoice data.

        Checks:
        - Tax calculation accuracy
        - Purchase order matching
        - Duplicate detection
        - Fraud indicators
        - Data completeness

        Args:
            state: Current processing state

        Returns:
            Updated state with validation results
        """
        errors: List[str] = []

        # 1. Validate tax calculation
        if not self._validate_tax_calculation(state):
            errors.append("Tax calculation mismatch")

        # 2. Validate amounts
        if not self._validate_amounts(state):
            errors.append("Amount validation failed")

        # 3. Check for required fields
        missing_fields = self._check_required_fields(state)
        if missing_fields:
            errors.extend([f"Missing field: {field}" for field in missing_fields])

        # 4. Check for duplicate
        if self._check_duplicate(state):
            errors.append("Duplicate invoice detected")
            state["duplicate_detected"] = True

        # 5. Fraud detection
        fraud_indicators = self._detect_fraud(state)
        if fraud_indicators:
            errors.extend(fraud_indicators)
            state["fraud_detected"] = True

        # 6. Purchase Order validation
        if state.get("po_number"):
            po_valid = self._validate_po(state)
            state["po_matched"] = po_valid
            if not po_valid:
                errors.append("Purchase Order mismatch or not found")

        # Update state
        state["validation_errors"] = errors
        state["is_valid"] = len(errors) == 0

        # Adjust confidence score based on validation
        if errors:
            state["confidence_score"] = max(0.0, state["confidence_score"] - (len(errors) * 0.1))

        # Determine if clarification is needed
        if errors and not state.get("fraud_detected"):
            state["clarification_needed"] = True
            state["clarification_message"] = "Invoice validation issues: " + "; ".join(errors)

        state["current_step"] = "validation_completed"

        return state

    def _validate_tax_calculation(self, state: InvoiceProcessingState) -> bool:
        """Validate tax calculation accuracy."""
        net = state.get("net_amount", 0)
        tax = state.get("tax_amount", 0)
        total = state.get("total_amount", 0)

        # Check if net + tax = total (with small margin for rounding)
        calculated_total = net + tax
        return abs(calculated_total - total) < 0.01

    def _validate_amounts(self, state: InvoiceProcessingState) -> bool:
        """Validate that amounts are positive and reasonable."""
        total = state.get("total_amount", 0)
        tax = state.get("tax_amount", 0)
        net = state.get("net_amount", 0)

        return total > 0 and tax >= 0 and net > 0

    def _check_required_fields(self, state: InvoiceProcessingState) -> List[str]:
        """Check for required fields."""
        required = [
            "invoice_number",
            "supplier_name",
            "invoice_date",
            "due_date",
            "total_amount"
        ]

        missing = []
        for field in required:
            if not state.get(field):
                missing.append(field)

        return missing

    def _check_duplicate(self, state: InvoiceProcessingState) -> bool:
        """
        Check for duplicate invoices.

        In production, query database for existing invoice with same number.
        """
        # Simulated check - in production, query database
        return False

    def _detect_fraud(self, state: InvoiceProcessingState) -> List[str]:
        """
        Detect potential fraud indicators.

        Checks for:
        - Unusual amounts
        - Suspicious supplier
        - Invalid dates
        - etc.
        """
        indicators = []

        # Check for suspiciously round numbers (simple heuristic)
        total = state.get("total_amount", 0)
        if total > 0 and total % 1000 == 0 and total > 10000:
            # This is just a demo heuristic
            pass

        # Check for future invoice dates
        invoice_date = state.get("invoice_date")
        if invoice_date and invoice_date > datetime.now():
            indicators.append("Invoice date is in the future")

        # Check for invalid due date
        due_date = state.get("due_date")
        if invoice_date and due_date and due_date < invoice_date:
            indicators.append("Due date is before invoice date")

        return indicators

    def _validate_po(self, state: InvoiceProcessingState) -> bool:
        """
        Validate purchase order matching.

        In production, this would:
        - Query PO from ERP system
        - Match items and amounts
        - Verify authorization
        """
        po_number = state.get("po_number")

        # Simulated PO validation
        # In production, query PO system
        if po_number and po_number.startswith("PO-"):
            state["po_data"] = {
                "po_number": po_number,
                "authorized_amount": state.get("total_amount", 0),
                "status": "approved"
            }
            return True

        return False


from datetime import datetime
