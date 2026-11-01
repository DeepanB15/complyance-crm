from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.model import Deal
from app.services.deal_service import process_closed_won_deal

router = APIRouter(prefix="/sync", tags=["Sync"])


@router.post("/deals/{deal_id}")
async def sync_deal(
    deal_id: UUID,
    db: Session = Depends(get_db),
):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()

    if not deal:
        raise HTTPException(
            status_code=404,
            detail="Deal not found",
        )

    if deal.stage != "Closed Won":
        raise HTTPException(
            status_code=400,
            detail="Deal is not Closed Won",
        )

    try:
        sales_order = await process_closed_won_deal(
            db=db,
            deal=deal,
        )

        return {
            "status": "success",
            "deal_id": str(deal.id),
            "sales_order_id": str(sales_order.id),
            "zoho_sales_order_id": sales_order.zoho_sales_order_id,
        }

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )