import asyncio
import time
import uuid

import httpx

from app.core.config import settings
from app.db.database import SessionLocal
from app.db.model import IntegrationLog
from app.integrations.zoho.auth import zoho_auth


class ZohoClient:

    async def request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ):
        start_time = time.time()
        event_id = str(uuid.uuid4())

        access_token = await zoho_auth.get_access_token()

        url = f"{settings.zoho_api_url}{endpoint}"

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Zoho-oauthtoken {access_token}"

        params = kwargs.pop("params", {})
        params["organization_id"] = settings.zoho_organization_id

        request_body = kwargs.get("json", {})

        response = None
        error_message = None
        status = "failed"

        try:
            # Retry transient failures and rate limits
            for attempt in range(3):
                try:
                    async with httpx.AsyncClient(
                        timeout=30.0
                    ) as client:

                        response = await client.request(
                            method,
                            url,
                            headers=headers,
                            params=params,
                            **kwargs,
                        )

                    # Rate limit / temporary server errors
                    if response.status_code in {
                        429,
                        500,
                        502,
                        503,
                        504,
                    }:

                        if attempt < 2:

                            retry_after = response.headers.get(
                                "Retry-After"
                            )

                            if retry_after:
                                try:
                                    delay = float(retry_after)
                                except ValueError:
                                    delay = 2 ** attempt
                            else:
                                delay = 2 ** attempt

                            await asyncio.sleep(delay)
                            continue

                    # Permanent API error
                    if response.status_code >= 400:
                        raise RuntimeError(
                            f"Zoho API error "
                            f"{response.status_code}: "
                            f"{response.text}"
                        )

                    status = "success"

                    return response.json()

                except (
                    httpx.TimeoutException,
                    httpx.NetworkError,
                ) as exc:

                    if attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                        continue

                    raise exc

            raise RuntimeError(
                "Zoho API request failed after 3 attempts"
            )

        except Exception as exc:
            error_message = str(exc)
            raise

        finally:
            # Record integration log
            duration_ms = int(
                (time.time() - start_time) * 1000
            )

            try:
                db = SessionLocal()

                log = IntegrationLog(
                    event_id=event_id,
                    system="zoho",
                    operation=f"{method} {endpoint}",
                    method=method,
                    endpoint=endpoint,
                    status_code=(
                        response.status_code
                        if response is not None
                        else None
                    ),
                    status=status,
                    request_summary=str(request_body)[:1000],
                    response_summary=(
                        response.text[:1000]
                        if response is not None
                        else None
                    ),
                    error_message=error_message,
                    duration_ms=duration_ms,
                )

                db.add(log)
                db.commit()
                db.close()

            except Exception as log_error:
                print(
                    "Failed to save integration log:",
                    log_error,
                )

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

        return await self.request(
            "POST",
            "/contacts",
            json=payload,
        )

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