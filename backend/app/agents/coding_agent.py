"""
Coding Agent for assigning GL accounts and cost centers.
"""
from typing import List, Dict, Any
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate

from app.core.config import settings
from app.agents.state import InvoiceProcessingState


class CodingAgent:
    """Agent responsible for accounting coding using AI."""

    def __init__(self):
        """Initialize coding agent."""
        self.llm = AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            deployment_name=settings.AZURE_OPENAI_DEPLOYMENT,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            temperature=0.1,
        )

        self.coding_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert accounting AI that assigns General Ledger (GL) accounts
            and cost centers to invoice line items.

            Use the following chart of accounts:
            - 5000: IT Services & Software
            - 5100: Professional Services
            - 5200: Office Supplies
            - 5300: Travel & Entertainment
            - 5400: Marketing & Advertising
            - 5500: Utilities
            - 5600: Rent & Facilities
            - 5700: Training & Development
            - 6000: Other Operating Expenses

            Cost Centers:
            - CC-100: Engineering
            - CC-200: Sales
            - CC-300: Marketing
            - CC-400: Operations
            - CC-500: Finance
            - CC-600: General & Administrative

            Based on the supplier name and line items, assign the most appropriate
            GL account and cost center. Return your reasoning."""),
            ("user", """Supplier: {supplier_name}
            Line Items: {line_items}

            Assign GL account and cost center with reasoning.""")
        ])

    def process(self, state: InvoiceProcessingState) -> InvoiceProcessingState:
        """
        Assign GL accounts and cost centers using AI.

        Args:
            state: Current processing state

        Returns:
            Updated state with accounting codes
        """
        try:
            supplier_name = state.get("supplier_name", "Unknown")
            line_items = state.get("line_items", [])

            # Use AI to determine appropriate coding
            chain = self.coding_prompt | self.llm
            response = chain.invoke({
                "supplier_name": supplier_name,
                "line_items": str(line_items)
            })

            # Parse AI response and assign codes
            # For demo, use simple logic
            gl_account, cost_center = self._determine_coding(supplier_name, line_items)

            state["gl_account"] = gl_account
            state["cost_center"] = cost_center

            # Create accounting entries
            state["accounting_entries"] = self._create_accounting_entries(state)

            state["current_step"] = "coding_completed"

        except Exception as e:
            state["processing_errors"].append(f"Coding error: {str(e)}")
            state["current_step"] = "coding_failed"

        return state

    def _determine_coding(self, supplier_name: str, line_items: List[Dict]) -> tuple:
        """
        Determine GL account and cost center.

        In production, this would use:
        - Historical coding patterns
        - ML model trained on past invoices
        - Supplier categorization
        """
        # Simple rule-based logic for demo
        supplier_lower = supplier_name.lower()

        # IT/Software vendors
        if any(keyword in supplier_lower for keyword in ["tech", "software", "cloud", "aws", "azure"]):
            return "5000", "CC-100"

        # Professional services
        elif any(keyword in supplier_lower for keyword in ["consulting", "legal", "audit"]):
            return "5100", "CC-600"

        # Marketing
        elif any(keyword in supplier_lower for keyword in ["marketing", "advertising", "media"]):
            return "5400", "CC-300"

        # Default
        else:
            return "6000", "CC-600"

    def _create_accounting_entries(self, state: InvoiceProcessingState) -> List[Dict[str, Any]]:
        """
        Create accounting entries for ERP integration.

        Standard double-entry:
        - Debit: Expense account
        - Credit: Accounts Payable
        """
        entries = []

        # Debit entry (expense)
        entries.append({
            "account": state["gl_account"],
            "cost_center": state["cost_center"],
            "debit": state["net_amount"],
            "credit": 0,
            "description": f"Invoice {state.get('invoice_number')} - {state.get('supplier_name')}"
        })

        # Tax entry (if applicable)
        if state.get("tax_amount", 0) > 0:
            entries.append({
                "account": "1500",  # Tax Receivable/Input VAT
                "cost_center": state["cost_center"],
                "debit": state["tax_amount"],
                "credit": 0,
                "description": f"Tax - Invoice {state.get('invoice_number')}"
            })

        # Credit entry (accounts payable)
        entries.append({
            "account": "2000",  # Accounts Payable
            "cost_center": state["cost_center"],
            "debit": 0,
            "credit": state["total_amount"],
            "description": f"AP - {state.get('supplier_name')}"
        })

        return entries
