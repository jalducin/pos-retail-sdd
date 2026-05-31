"""Fixtures pytest: SQLite en memoria con esquema cargado desde Base.metadata.

Sustituye la dependencia `get_db` de FastAPI por una sesión bound al engine en memoria.
"""
from decimal import Decimal
from typing import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.branch import Branch
from app.models.product import Product
from app.models.user import User, UserRole


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )

    @event.listens_for(eng, "connect")
    def _fk(dbapi_connection, _):
        cur = dbapi_connection.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def db_session(engine) -> Iterator[Session]:
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = session_factory()
    try:
        yield session
    finally:
        session.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()


@pytest.fixture
def client(db_session) -> Iterator[TestClient]:
    def _override_get_db() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def seeded_users(db_session) -> dict[str, User]:
    branch = Branch(name="Test Branch", timezone="America/Mexico_City")
    db_session.add(branch)
    db_session.flush()
    admin = User(
        name="Admin",
        email="admin@test.com",
        password_hash=hash_password("adminpw"),
        role=UserRole.admin,
        branch_id=branch.id,
    )
    cashier = User(
        name="Cashier",
        email="cashier@test.com",
        password_hash=hash_password("cashpw"),
        role=UserRole.cashier,
        branch_id=branch.id,
    )
    db_session.add_all([admin, cashier])
    db_session.commit()
    return {"admin": admin, "cashier": cashier, "branch": branch}


@pytest.fixture
def seeded_product(db_session) -> Product:
    product = Product(sku="TEST-001", name="Producto de prueba", price=Decimal("100.00"), stock=10, category="Test")
    db_session.add(product)
    db_session.commit()
    return product
