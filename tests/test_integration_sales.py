"""Tests de integración: login → producto → venta → consulta.

Cubre CA-01.1, CA-01.2, CA-01.3, CA-03.1, CA-03.2 con SQLite en memoria.
"""
from decimal import Decimal


def _login(client, email: str, password: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_login_emite_jwt(client, seeded_users):
    token = _login(client, "admin@test.com", "adminpw")
    assert isinstance(token, str) and len(token) > 20


def test_login_credenciales_invalidas_devuelve_AUTH_REQUIRED(client, seeded_users):
    response = client.post("/auth/login", json={"email": "admin@test.com", "password": "wrong"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_REQUIRED"


def test_admin_crea_producto_y_cajero_lo_lista(client, seeded_users):
    admin_token = _login(client, "admin@test.com", "adminpw")
    cashier_token = _login(client, "cashier@test.com", "cashpw")

    create = client.post(
        "/products",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"sku": "SKU-X", "name": "Coca 600", "price": "18.00", "stock": 20, "category": "Bebidas"},
    )
    assert create.status_code == 201, create.text

    listed = client.get("/products", headers={"Authorization": f"Bearer {cashier_token}"})
    assert listed.status_code == 200
    assert any(p["sku"] == "SKU-X" for p in listed.json())


def test_cajero_no_puede_crear_producto_FORBIDDEN(client, seeded_users):
    cashier_token = _login(client, "cashier@test.com", "cashpw")
    response = client.post(
        "/products",
        headers={"Authorization": f"Bearer {cashier_token}"},
        json={"sku": "SKU-Z", "name": "X", "price": "10", "stock": 1},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_venta_efectivo_CA_01_1_descuenta_stock(client, seeded_users, seeded_product):
    cashier_token = _login(client, "cashier@test.com", "cashpw")
    response = client.post(
        "/sales",
        headers={"Authorization": f"Bearer {cashier_token}"},
        json={
            "items": [{"product_id": str(seeded_product.id), "quantity": 2}],
            "payment_method": "cash",
            "cash_received": "300.00",
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert Decimal(body["subtotal"]) == Decimal("200.00")
    assert Decimal(body["tax"]) == Decimal("32.00")
    assert Decimal(body["total"]) == Decimal("232.00")
    assert Decimal(body["change_given"]) == Decimal("68.00")
    assert body["status"] == "completed"

    fresh = client.get("/products", headers={"Authorization": f"Bearer {cashier_token}"})
    products = {p["sku"]: p for p in fresh.json()}
    assert products["TEST-001"]["stock"] == 8


def test_venta_sin_stock_CA_01_2_responde_409(client, seeded_users, seeded_product):
    cashier_token = _login(client, "cashier@test.com", "cashpw")
    response = client.post(
        "/sales",
        headers={"Authorization": f"Bearer {cashier_token}"},
        json={
            "items": [{"product_id": str(seeded_product.id), "quantity": 999}],
            "payment_method": "cash",
            "cash_received": "100000",
        },
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "STOCK_INSUFFICIENT"


def test_idempotency_key_devuelve_misma_venta(client, seeded_users, seeded_product):
    cashier_token = _login(client, "cashier@test.com", "cashpw")
    payload = {
        "items": [{"product_id": str(seeded_product.id), "quantity": 1}],
        "payment_method": "cash",
        "cash_received": "200",
    }
    headers = {"Authorization": f"Bearer {cashier_token}", "Idempotency-Key": "test-key-001"}

    first = client.post("/sales", headers=headers, json=payload)
    second = client.post("/sales", headers=headers, json=payload)
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
