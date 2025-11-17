"""
OCR Agent for extracting data from invoices.
"""
import json
from typing import Dict, Any
from datetime import datetime
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate

from app.core.config import settings
from app.agents.state import InvoiceProcessingState


class OCRAgent:
    """Agent responsible for extracting data from invoice documents."""

    def __init__(self):
        """Initialize OCR agent with Azure OpenAI."""
        self.llm = AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            deployment_name=settings.AZURE_OPENAI_DEPLOYMENT,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            temperature=0.1,
        )

        self.extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert invoice data extraction AI.
            Extract all relevant information from the invoice with 99%+ accuracy.

            Extract the following fields:
            - invoice_number
            - supplier_name
            - supplier_tax_id
            - invoice_date (ISO format)
            - due_date (ISO format)
            - total_amount (numeric)
            - tax_amount (numeric)
            - net_amount (numeric)
            - currency (ISO code)
            - po_number (if present)
            - line_items (array of items with description, quantity, unit_price, total)

            Return ONLY valid JSON with these fields. If a field is not found, use null.
            Be precise with numbers and dates."""),
            ("user", "Extract data from this invoice:\n\n{invoice_text}")
        ])

    def process(self, state: InvoiceProcessingState) -> InvoiceProcessingState:
        """
        Extract data from invoice document.

        Args:
            state: Current processing state

        Returns:
            Updated state with extracted data
        """
        try:
            # Simulate document text extraction
            # In production, use LlamaParse or Azure Document Intelligence
            invoice_text = self._extract_text(state["document_path"])

            # Extract structured data using LLM
            chain = self.extraction_prompt | self.llm
            response = chain.invoke({"invoice_text": invoice_text})

            # Parse extracted data
            extracted_data = json.loads(response.content)

            # Update state with extracted data
            state["invoice_number"] = extracted_data.get("invoice_number")
            state["supplier_name"] = extracted_data.get("supplier_name")
            state["supplier_tax_id"] = extracted_data.get("supplier_tax_id")
            state["total_amount"] = float(extracted_data.get("total_amount", 0))
            state["tax_amount"] = float(extracted_data.get("tax_amount", 0))
            state["net_amount"] = float(extracted_data.get("net_amount", 0))
            state["currency"] = extracted_data.get("currency", "USD")
            state["po_number"] = extracted_data.get("po_number")
            state["line_items"] = extracted_data.get("line_items", [])

            # Parse dates
            if extracted_data.get("invoice_date"):
                state["invoice_date"] = datetime.fromisoformat(extracted_data["invoice_date"])
            if extracted_data.get("due_date"):
                state["due_date"] = datetime.fromisoformat(extracted_data["due_date"])

            # Set confidence score (high for structured extraction)
            state["confidence_score"] = 0.98
            state["current_step"] = "ocr_completed"

        except Exception as e:
            state["processing_errors"].append(f"OCR error: {str(e)}")
            state["confidence_score"] = 0.0
            state["current_step"] = "ocr_failed"

        return state

    def _extract_text(self, document_path: str) -> str:
        """
        Extract text from document.

        In production, this would use:
        - LlamaParse for complex PDFs
        - Azure Document Intelligence
        - OCR libraries

        For now, returns simulated data.
        """
        # Simulated invoice text for demo
        return """
        INVOICE

        Invoice Number: INV-2024-001
        Invoice Date: 2024-01-15
        Due Date: 2024-02-15

        Supplier:
        Tech Solutions Inc.
        Tax ID: 12-3456789

        Bill To:
        PERFO Corporation

        Items:
        1. Cloud Services - Monthly Subscription
           Quantity: 1
           Unit Price: $1,500.00
           Total: $1,500.00

        2. Support Package - Premium
           Quantity: 1
           Unit Price: $500.00
           Total: $500.00

        Subtotal: $2,000.00
        Tax (10%): $200.00
        Total: $2,200.00

        Purchase Order: PO-2024-045

        Payment Terms: Net 30
        Early Payment Discount: 2% if paid within 10 days
        """
