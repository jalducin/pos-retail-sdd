import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_claims, require_roles
from app.core.errors import NotFound
from app.models.branch import Branch
from app.models.user import UserRole
from app.schemas.branch import BranchCreate, BranchOut, BranchUpdate

router = APIRouter(prefix="/branches", tags=["branches"])


@router.get("", response_model=list[BranchOut])
def list_branches(
    db: Session = Depends(db_session),
    _claims: dict = Depends(get_current_claims),
    include_inactive: bool = False,
) -> list[Branch]:
    stmt = select(Branch)
    if not include_inactive:
        stmt = stmt.where(Branch.is_active.is_(True))
    return list(db.execute(stmt.order_by(Branch.name)).scalars())


@router.post("", response_model=BranchOut, status_code=status.HTTP_201_CREATED)
def create_branch(
    payload: BranchCreate,
    db: Session = Depends(db_session),
    _claims: dict = Depends(require_roles(UserRole.admin)),
) -> Branch:
    branch = Branch(**payload.model_dump())
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return branch


@router.put("/{branch_id}", response_model=BranchOut)
def update_branch(
    branch_id: uuid.UUID,
    payload: BranchUpdate,
    db: Session = Depends(db_session),
    _claims: dict = Depends(require_roles(UserRole.admin)),
) -> Branch:
    branch = db.get(Branch, branch_id)
    if branch is None:
        raise NotFound("Sucursal no encontrada")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(branch, field, value)
    db.commit()
    db.refresh(branch)
    return branch
