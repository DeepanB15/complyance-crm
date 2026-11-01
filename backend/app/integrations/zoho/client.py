import httpx

from app.core.config import settings
from app.integrations.zoho.auth import zoho_auth


class ZohoClient:

    async def request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ):
        access_token = await zoho_auth.get_access_token()

        url = f"{settings.zoho_api_url}{endpoint}"

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Zoho-oauthtoken {access_token}"

        params = kwargs.pop("params", {})
        params["organization_id"] = settings.zoho_organization_id

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                url,
                headers=headers,
                params=params,
                **kwargs,
            )

        # Debug information for Zoho API responses
        print("ZOHO API STATUS:", response.status_code)
        print("ZOHO API RESPONSE:", response.text)

        # Do not hide Zoho's actual error message
        if response.status_code >= 400:
            raise RuntimeError(
                f"Zoho API error {response.status_code}: {response.text}"
            )

        return response.json()

    async def get_organizations(self):
        return await self.request(
            "GET",
            "/organizations",
        )

    async def search_customers(
        self,
        email: str | None = None,
        name: str | None = None,
    ):
        params = {}

        if email:
            params["email"] = email

        if name:
            params["customer_name"] = name

        return await self.request(
            "GET",
            "/contacts",
            params=params,
        )

    async def create_customer(
        self,
        name: str,
        email: str,
        phone: str | None = None,
    ):
        payload = {
            "contact_name": name,
            "contact_type": "customer",
            "email": email,
        }

        if phone:
            payload["phone"] = phone

        print("ZOHO CREATE CUSTOMER PAYLOAD:", payload)

        result = await self.request(
            "POST",
            "/contacts",
            json=payload,
        )

        print("ZOHO CREATE CUSTOMER RESPONSE:", result)

        return result

    async def list_items(self):
        return await self.request(
            "GET",
            "/items",
        )

    async def create_item(
        self,
        name: str,
        rate: float,
        description: str = "",
    ):
        payload = {
            "name": name,
            "rate": rate,
            "description": description,
        }

        return await self.request(
            "POST",
            "/items",
            json=payload,
        )

    async def create_sales_order(
        self,
        customer_id: str,
        reference_number: str,
        item_id: str,
        quantity: float,
        rate: float,
        currency_code: str = "INR",
    ):
        payload = {
            "customer_id": customer_id,
            "reference_number": reference_number,
            "currency_code": currency_code,
            "line_items": [
                {
                    "item_id": item_id,
                    "quantity": quantity,
                    "rate": rate,
                }
            ],
        }

        return await self.request(
            "POST",
            "/salesorders",
            json=payload,
        )

    async def create_invoice_from_sales_order(
        self,
        customer_id: str,
        sales_order_id: str,
        amount: float,
    ):
        payload = {
            "customer_id": customer_id,
            "salesorder_id": sales_order_id,
            "line_items": [
                {
                    "item_id": "4339701000000034168",
                    "quantity": 1,
                    "rate": amount,
                }
            ],
        }

        return await self.request(
            "POST",
            "/invoices",
            json=payload,
        )

    async def create_customer_payment(
        self,
        customer_id: str,
        invoice_id: str,
        amount: float,
    ):
        payload = {
            "customer_id": customer_id,
            "amount": amount,
            "payment_mode": "cash",
            "reference_number": "PAY-DEMO-001",
            "invoices": [
                {
                    "invoice_id": invoice_id,
                    "amount_applied": amount,
                }
            ],
        }

        return await self.request(
            "POST",
            "/customerpayments",
            json=payload,
        )


zoho_client = ZohoClient()