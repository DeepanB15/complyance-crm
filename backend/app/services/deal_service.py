from decimal import Decimal

from sqlalchemy.orm import Session

from app.db.model import Deal, SalesOrder, Invoice, Payment
from app.integrations.zoho.service import zoho_service


async def process_closed_won_deal(
    db: Session,
    deal: Deal,
):
    # Idempotency
    existing_order = (
        db.query(SalesOrder)
        .filter(SalesOrder.deal_id == deal.id)
        .first()
    )

    if existing_order:
        return existing_order

    customer = deal.customer

    # 1. Find/create Zoho customer
    zoho_customer = await zoho_service.find_or_create_customer(
        name=customer.name,
        email=customer.email or "",
        phone=customer.phone,
    )

    zoho_customer_id = zoho_customer.get("contact_id")

    if not zoho_customer_id:
        raise RuntimeError("Zoho customer ID was not returned")

    customer.zoho_customer_id = zoho_customer_id

    # 2. Create Sales Order
    amount = Decimal(str(deal.amount))

    sales_order_result = await zoho_service.create_sales_order(
        customer_id=zoho_customer_id,
        reference_number=f"CRM-{deal.crm_deal_id}",
        item_id="4339701000000034168",
        amount=amount,
        currency_code=deal.currency or "INR",
    )

    zoho_sales_order = sales_order_result.get("salesorder", {})
    zoho_sales_order_id = zoho_sales_order.get("salesorder_id")

    if not zoho_sales_order_id:
        raise RuntimeError("Zoho Sales Order ID was not returned")

    sales_order = SalesOrder(
        deal_id=deal.id,
        zoho_sales_order_id=zoho_sales_order_id,
        order_number=zoho_sales_order.get("salesorder_number"),
        subtotal=amount,
        tax_amount=Decimal("0"),
        total=amount,
        currency=deal.currency or "INR",
        status=zoho_sales_order.get("status", "draft"),
    )

    db.add(sales_order)
    db.flush()

    # 3. Create milestone invoices
    milestones = [
        Decimal("50"),
        Decimal("30"),
        Decimal("20"),
    ]

    created_invoices = []

    for percentage in milestones:
        milestone_amount = (
            amount * percentage / Decimal("100")
        ).quantize(Decimal("0.01"))

        invoice_result = await zoho_service.create_milestone_invoice(
            customer_id=zoho_customer_id,
            sales_order_id=zoho_sales_order_id,
            item_id="4339701000000034168",
            amount=milestone_amount,
        )

        zoho_invoice = invoice_result.get("invoice", {})

        invoice = Invoice(
            sales_order_id=sales_order.id,
            zoho_invoice_id=zoho_invoice.get("invoice_id"),
            invoice_number=zoho_invoice.get("invoice_number"),
            milestone_percentage=percentage,
            subtotal=milestone_amount,
            tax_amount=Decimal("0"),
            total=milestone_amount,
            amount_paid=Decimal("0"),
            status=zoho_invoice.get("status", "draft"),
        )

        db.add(invoice)
        created_invoices.append(invoice)

    db.flush()

    # 4. Record first milestone payment
    first_invoice = created_invoices[0]

    payment_result = await zoho_service.record_payment(
        customer_id=zoho_customer_id,
        invoice_id=first_invoice.zoho_invoice_id,
        amount=first_invoice.total,
    )

    zoho_payment = payment_result.get("payment", {})

    payment = Payment(
        zoho_payment_id=zoho_payment.get("payment_id"),
        invoice_id=first_invoice.id,
        amount=first_invoice.total,
        currency=deal.currency or "INR",
    )

    db.add(payment)

    first_invoice.amount_paid = first_invoice.total
    first_invoice.status = "paid"

    db.commit()

    return sales_order