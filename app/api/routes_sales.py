import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_claims, require_roles
from app.core.errors import NotFound
from app.models.sale import Sale
from app.models.user import UserRole
from app.schemas.sale import SaleCreate, SaleOut
from app.services.sales_service import process_sale

router = APIRouter(prefix="/sales", tags=["sales"])


@router.post("", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
def create_sale(
    payload: SaleCreate,
    db: Session = Depends(db_session),
    claims: dict = Depends(get_current_claims),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key", max_length=64),
) -> Sale:
    cashier_id = uuid.UUID(claims["sub"])
    branch_id = uuid.UUID(claims["branch_id"]) if claims.get("branch_id") else None
    return process_sale(
        db=db,
        cashier_id=cashier_id,
        branch_id=branch_id,
        payload=payload,
        idempotency_key=idempotency_key,
    )


@router.get("", response_model=list[SaleOut])
def list_sales(
    db: Session = Depends(db_session),
    _claims: dict = Depends(require_roles(UserRole.supervisor, UserRole.admin)),
    cashier_id: uuid.UUID | None = None,
    date_from: datetime | None = Query(default=None, alias="from"),
    date_to: datetime | None = Query(default=None, alias="to"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[Sale]:
    stmt = select(Sale).order_by(Sale.created_at.desc())
    if cashier_id is not None:
        stmt = stmt.where(Sale.cashier_id == cashier_id)
    if date_from is not None:
        stmt = stmt.where(Sale.created_at >= date_from)
    if date_to is not None:
        stmt = stmt.where(Sale.created_at <= date_to)
    return list(db.execute(stmt.limit(limit).offset(offset)).scalars())


@router.get("/{sale_id}", response_model=SaleOut)
def get_sale(sale_id: uuid.UUID, db: Session = Depends(db_session), _claims: dict = Depends(get_current_claims)) -> Sale:
    sale = db.get(Sale, sale_id)
    if sale is None:
        raise NotFound("Venta no encontrada")
    return sale
