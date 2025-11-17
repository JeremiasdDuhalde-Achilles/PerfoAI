"""
Database initialization script with seed data.
"""
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models.user import User
from app.models.supplier import Supplier
from app.models.invoice import Invoice
from datetime import datetime, timedelta


def init_db(db: Session) -> None:
    """Initialize database with seed data."""

    # Create users with different roles
    users = [
        User(
            email="admin@perfo.ai",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            role="admin",
            is_active=True
        ),
        User(
            email="finance@perfo.ai",
            username="finance_manager",
            hashed_password=get_password_hash("finance123"),
            full_name="Finance Manager",
            role="finance_manager",
            is_active=True
        ),
        User(
            email="approver@perfo.ai",
            username="approver",
            hashed_password=get_password_hash("approver123"),
            full_name="Invoice Approver",
            role="approver",
            is_active=True
        ),
        User(
            email="viewer@perfo.ai",
            username="viewer",
            hashed_password=get_password_hash("viewer123"),
            full_name="Read Only User",
            role="viewer",
            is_active=True
        ),
    ]

    for user in users:
        existing_user = db.query(User).filter(User.username == user.username).first()
        if not existing_user:
            db.add(user)

    db.commit()

    # Create sample suppliers
    suppliers = [
        Supplier(
            name="Tech Solutions Inc.",
            tax_id="12-3456789",
            email="billing@techsolutions.com",
            phone="+1-555-0100",
            address="123 Tech Street, Silicon Valley, CA 94000",
            country="USA",
            is_active=True,
            is_verified=True,
            risk_score=15
        ),
        Supplier(
            name="Cloud Services Corp",
            tax_id="98-7654321",
            email="accounts@cloudservices.com",
            phone="+1-555-0200",
            address="456 Cloud Avenue, Seattle, WA 98000",
            country="USA",
            is_active=True,
            is_verified=True,
            risk_score=10
        ),
        Supplier(
            name="Office Supplies Ltd",
            tax_id="45-6789012",
            email="orders@officesupplies.com",
            phone="+1-555-0300",
            address="789 Supply Road, New York, NY 10000",
            country="USA",
            is_active=True,
            is_verified=True,
            risk_score=5
        ),
    ]

    for supplier in suppliers:
        existing_supplier = db.query(Supplier).filter(Supplier.tax_id == supplier.tax_id).first()
        if not existing_supplier:
            db.add(supplier)

    db.commit()

    # Create sample invoices
    invoices = [
        Invoice(
            invoice_number="INV-2024-001",
            supplier_id=1,
            invoice_date=datetime.now() - timedelta(days=5),
            due_date=datetime.now() + timedelta(days=25),
            total_amount=2200.00,
            tax_amount=200.00,
            net_amount=2000.00,
            currency="USD",
            po_number="PO-2024-001",
            po_matched=True,
            status="approved",
            processing_status="completed",
            confidence_score=0.98,
            is_touchless=True,
            gl_account="5000",
            cost_center="CC-100",
            approval_status="approved",
            approved_by=1,
            approved_at=datetime.now() - timedelta(days=4),
            document_format="pdf"
        ),
        Invoice(
            invoice_number="INV-2024-002",
            supplier_id=2,
            invoice_date=datetime.now() - timedelta(days=3),
            due_date=datetime.now() + timedelta(days=27),
            total_amount=5500.00,
            tax_amount=500.00,
            net_amount=5000.00,
            currency="USD",
            po_number="PO-2024-002",
            po_matched=True,
            status="pending",
            processing_status="pending_approval",
            confidence_score=0.96,
            is_touchless=False,
            gl_account="5000",
            cost_center="CC-100",
            approval_status="pending",
            document_format="pdf"
        ),
        Invoice(
            invoice_number="INV-2024-003",
            supplier_id=3,
            invoice_date=datetime.now() - timedelta(days=2),
            due_date=datetime.now() + timedelta(days=28),
            total_amount=880.00,
            tax_amount=80.00,
            net_amount=800.00,
            currency="USD",
            po_number="PO-2024-003",
            po_matched=True,
            status="approved",
            processing_status="completed",
            confidence_score=0.99,
            is_touchless=True,
            gl_account="5200",
            cost_center="CC-600",
            approval_status="approved",
            approved_by=2,
            approved_at=datetime.now() - timedelta(days=1),
            document_format="pdf"
        ),
        Invoice(
            invoice_number="INV-2024-004",
            supplier_id=1,
            invoice_date=datetime.now() - timedelta(days=1),
            due_date=datetime.now() + timedelta(days=29),
            total_amount=3300.00,
            tax_amount=300.00,
            net_amount=3000.00,
            currency="USD",
            po_number=None,
            po_matched=False,
            status="pending",
            processing_status="pending_clarification",
            confidence_score=0.85,
            is_touchless=False,
            validation_errors=["Purchase Order not found"],
            gl_account="5000",
            cost_center="CC-100",
            approval_status="pending",
            document_format="pdf"
        ),
    ]

    for invoice in invoices:
        existing_invoice = db.query(Invoice).filter(
            Invoice.invoice_number == invoice.invoice_number
        ).first()
        if not existing_invoice:
            db.add(invoice)

    db.commit()

    print("✅ Database initialized with seed data")
    print("\n👤 Test Users:")
    print("   Admin:           username='admin'            password='admin123'")
    print("   Finance Manager: username='finance_manager'  password='finance123'")
    print("   Approver:        username='approver'         password='approver123'")
    print("   Viewer:          username='viewer'           password='viewer123'")
    print("\n📊 Sample Data:")
    print("   - 4 Users")
    print("   - 3 Suppliers")
    print("   - 4 Invoices")
