from fastapi import FastAPI

app = FastAPI(
    title="Complyance CRM-Zoho Integration",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "crm-zoho-integration"
    }