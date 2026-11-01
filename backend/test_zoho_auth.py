import asyncio

from app.integrations.zoho.auth import zoho_auth


async def main():
    token = await zoho_auth.get_access_token()

    print("Zoho authentication successful")
    print("Access token received:", bool(token))


if __name__ == "__main__":
    asyncio.run(main())