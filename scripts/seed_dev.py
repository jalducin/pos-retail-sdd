"""Seed mínimo para desarrollo local. Idempotente: si ya hay admin, no duplica.

Uso:
    python -m scripts.seed_dev
"""
from decimal import Decimal

from sqlalchemy import select

from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models.branch import Branch
from app.models.product import Product
from app.models.user import User, UserRole

_PRODUCTS = [
    ("SKU-001", "Refresco 600ml", Decimal("18.00"), 100, "Bebidas", "7501055309856"),
    ("SKU-002", "Pan Bimbo grande", Decimal("52.00"), 40, "Panadería", "7501030450012"),
    ("SKU-003", "Leche entera 1L", Decimal("29.50"), 60, "Lácteos", "7501055304011"),
    ("SKU-004", "Café molido 250g", Decimal("89.00"), 25, "Abarrotes", "7501055310012"),
    ("SKU-005", "Tortillas 1kg", Decimal("32.00"), 80, "Tortillería", "7501055320120"),
]


def main() -> None:
    db = SessionLocal()
    try:
        branch = db.execute(select(Branch).where(Branch.name == "Sucursal Centro")).scalar_one_or_none()
        if branch is None:
            branch = Branch(name="Sucursal Centro", address="Av. Reforma 100, CDMX", timezone="America/Mexico_City")
            db.add(branch)
            db.flush()
            print(f"+ Branch creada: {branch.id}")

        admin = db.execute(select(User).where(User.email == "admin@pos.local")).scalar_one_or_none()
        if admin is None:
            admin = User(
                name="Admin Local",
                email="admin@pos.local",
                password_hash=hash_password("admin123"),
                role=UserRole.admin,
                branch_id=branch.id,
            )
            db.add(admin)
            print("+ Admin creado: admin@pos.local / admin123")

        cashier = db.execute(select(User).where(User.email == "cajero@pos.local")).scalar_one_or_none()
        if cashier is None:
            cashier = User(
                name="Cajero Demo",
                email="cajero@pos.local",
                password_hash=hash_password("cajero123"),
                role=UserRole.cashier,
                branch_id=branch.id,
            )
            db.add(cashier)
            print("+ Cajero creado: cajero@pos.local / cajero123")

        created_products = 0
        for sku, name, price, stock, category, barcode in _PRODUCTS:
            exists = db.execute(select(Product).where(Product.sku == sku)).scalar_one_or_none()
            if exists is None:
                db.add(Product(sku=sku, name=name, price=price, stock=stock, category=category, barcode=barcode))
                created_products += 1
        if created_products:
            print(f"+ {created_products} producto(s) creados")

        db.commit()
        print("Seed completado.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
