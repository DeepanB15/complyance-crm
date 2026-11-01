from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.model import IntegrationLog

router = APIRouter(prefix="/logs", tags=["Integration Logs"])


@router.get("")
def get_logs(
    db: Session = Depends(get_db),
):
    logs = (
        db.query(IntegrationLog)
        .order_by(IntegrationLog.created_at.desc())
        .limit(100)
        .all()
    )

    return [
        {
            "id": str(log.id),
            "deal_id": str(log.deal_id) if log.deal_id else None,
            "event_id": log.event_id,
            "system": log.system,
            "operation": log.operation,
            "method": log.method,
            "endpoint": log.endpoint,
            "status_code": log.status_code,
            "status": log.status,
            "error_message": log.error_message,
            "duration_ms": log.duration_ms,
            "created_at": log.created_at,
        }
        for log in logs
    ]