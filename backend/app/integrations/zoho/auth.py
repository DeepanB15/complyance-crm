import time

import httpx

from app.core.config import settings


class ZohoAuth:
    def __init__(self):
        self.access_token = None
        self.expires_at = 0

    async def get_access_token(self) -> str:
        # Reuse token if still valid
        if self.access_token and time.time() < self.expires_at - 60:
            return self.access_token

        url = f"{settings.zoho_accounts_url}/oauth/v2/token"

        data = {
            "refresh_token": settings.zoho_refresh_token,
            "client_id": settings.zoho_client_id,
            "client_secret": settings.zoho_client_secret,
            "grant_type": "refresh_token",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)

        response.raise_for_status()

        token_data = response.json()

        if "access_token" not in token_data:
            print("Zoho token response error:", token_data)
            raise RuntimeError("Zoho did not return an access token")

        self.access_token = token_data["access_token"]

        expires_in = token_data.get("expires_in", 3600)
        self.expires_at = time.time() + expires_in

        return self.access_token


zoho_auth = ZohoAuth()