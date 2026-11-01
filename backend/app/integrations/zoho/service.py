from decimal import Decimal

from app.integrations.zoho.client import zoho_client


class ZohoService:

    async def find_or_create_customer(
        self,
        name,
        email,
        phone=None,
    ):
        # 1. Search by email
        result = await zoho_client.search_customers(
            email=email,
        )

        print("ZOHO EMAIL SEARCH RESPONSE:", result)

        contacts = result.get("contacts", [])

        if contacts:
            print("CUSTOMER FOUND BY EMAIL")
            return contacts[0]

        # 2. Search by customer name
        result = await zoho_client.search_customers(
            name=name,
        )

        print("ZOHO NAME SEARCH RESPONSE:", result)

        contacts = result.get("contacts", [])

        if contacts:
            print("CUSTOMER FOUND BY NAME")
            return contacts[0]

        # 3. Create customer only if it doesn't exist
        result = await zoho_client.create_customer(
            name=name,
            email=email,
            phone=phone,
        )

        print("ZOHO CREATE CUSTOMER RESPONSE:", result)

        return result

    async def create_sales_order(
        self,
        customer_id: str,
        reference_number: str,
        item_id: str,
        amount: Decimal,
        currency_code: str = "INR",
    ):
        return await zoho_client.create_sales_order(
            customer_id=customer_id,
            reference_number=reference_number,
            item_id=item_id,
            quantity=1,
            rate=float(amount),
            currency_code=currency_code,
        )

    async def create_milestone_invoice(
        self,
        customer_id: str,
        sales_order_id: str,
        item_id: str,
        amount: Decimal,
    ):
        return await zoho_client.create_invoice_from_sales_order(
            customer_id=customer_id,
            sales_order_id=sales_order_id,
            amount=float(amount),
        )

    async def record_payment(
        self,
        customer_id: str,
        invoice_id: str,
        amount: Decimal,
    ):
        return await zoho_client.create_customer_payment(
            customer_id=customer_id,
            invoice_id=invoice_id,
            amount=float(amount),
        )


zoho_service = ZohoService()