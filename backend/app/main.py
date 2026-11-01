from fastapi import FastAPI
from app.api.routes.sync import router as sync_router
app = FastAPI(
    title="Complyance CRM-Zoho Integration",
    version="1.0.0",
)
app.include_router(sync_router)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "crm-zoho-integration"
    }