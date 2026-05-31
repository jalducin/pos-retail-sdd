from datetime import date, datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import db_session, require_roles
from app.core.config import get_settings
from app.models.sale import PaymentMethod, Sale, SaleStatus
from app.models.user import UserRole

router = APIRouter(prefix="/reports", tags=["reports"])


def _day_window_mx(target: date | None) -> tuple[datetime, datetime]:
    """Convierte un date local MX a un intervalo UTC [start, end_exclusive)."""
    tz = ZoneInfo(get_settings().timezone)
    today = target or datetime.now(tz).date()
    start_local = datetime.combine(today, time.min, tzinfo=tz)
    end_local = start_local + timedelta(days=1)
    return start_local, end_local


@router.get("/daily")
def daily_report(
    db: Session = Depends(db_session),
    _claims: dict = Depends(require_roles(UserRole.supervisor, UserRole.admin)),
    target_date: date | None = Query(default=None, alias="date"),
) -> dict:
    """Corte del día (TZ America/Mexico_City). Cubre FR-05 / CA-05.1."""
    start, end = _day_window_mx(target_date)

    rows = list(
        db.execute(
            select(
                Sale.payment_method,
                func.count(Sale.id),
                func.coalesce(func.sum(Sale.total), 0),
            )
            .where(Sale.created_at >= start, Sale.created_at < end, Sale.status == SaleStatus.completed)
            .group_by(Sale.payment_method)
        )
    )

    by_method: dict[str, dict] = {}
    total_count = 0
    total_amount = Decimal("0")
    for method, count, amount in rows:
        method_key = method.value if isinstance(method, PaymentMethod) else str(method)
        amount_dec = Decimal(str(amount))
        by_method[method_key] = {"count": int(count), "amount": str(amount_dec)}
        total_count += int(count)
        total_amount += amount_dec

    return {
        "date": (target_date or start.date()).isoformat(),
        "timezone": get_settings().timezone,
        "totals": {"tickets": total_count, "amount": str(total_amount)},
        "by_payment_method": by_method,
    }
