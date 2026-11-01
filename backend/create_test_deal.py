from decimal import Decimal

from app.db.database import SessionLocal
from app.db.model import Customer, Deal


db = SessionLocal()

try:
    customer = Customer(
        crm_customer_id="CRM-CUST-DEMO-001",
        name="Demo Integration Customer",
        email="demo.customer@example.com",
        phone="+919876543210",
        currency="INR",
    )

    db.add(customer)
    db.flush()

    deal = Deal(
        crm_deal_id="CRM-DEAL-DEMO-001",
        customer_id=customer.id,
        name="CRM Implementation Deal",
        stage="Closed Won",
        currency="INR",
        amount=Decimal("120000.00"),
        tax_rate=Decimal("0.00"),
    )

    db.add(deal)
    db.commit()

    print("Customer ID:", customer.id)
    print("Deal ID:", deal.id)

finally:
    db.close()