import asyncio

from app.integrations.zoho.client import zoho_client


async def main():
    result = await zoho_client.create_customer_payment(
        customer_id="4339701000000039002",
        invoice_id="4339701000000043001",
        amount=60000,
    )

    print("Payment API successful")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())