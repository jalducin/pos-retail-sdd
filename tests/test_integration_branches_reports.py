"""Integración: /branches, GET /sales (list), /reports/daily."""
from datetime import datetime, timedelta, timezone


def _login(client, email, password):
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_admin_crea_y_lista_branches(client, seeded_users):
    admin = _login(client, "admin@test.com", "adminpw")
    create = client.post(
        "/branches", headers=_auth(admin), json={"name": "Sucursal Norte", "address": "Av. Norte 1", "timezone": "America/Mexico_City"}
    )
    assert create.status_code == 201, create.text

    listed = client.get("/branches", headers=_auth(admin))
    assert listed.status_code == 200
    names = {b["name"] for b in listed.json()}
    assert {"Test Branch", "Sucursal Norte"} <= names


def test_cajero_no_puede_crear_branch_FORBIDDEN(client, seeded_users):
    cashier = _login(client, "cashier@test.com", "cashpw")
    r = client.post("/branches", headers=_auth(cashier), json={"name": "X"})
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "FORBIDDEN"


def test_admin_edita_branch(client, seeded_users):
    admin = _login(client, "admin@test.com", "adminpw")
    listed = client.get("/branches", headers=_auth(admin)).json()
    bid = listed[0]["id"]
    upd = client.put("/branches/" + bid, headers=_auth(admin), json={"address": "Nueva dirección"})
    assert upd.status_code == 200
    assert upd.json()["address"] == "Nueva dirección"


def test_list_sales_requiere_supervisor_o_admin(client, seeded_users, seeded_product):
    cashier = _login(client, "cashier@test.com", "cashpw")
    admin = _login(client, "admin@test.com", "adminpw")

    # cajero vende una vez
    client.post(
        "/sales",
        headers=_auth(cashier),
        json={"items": [{"product_id": str(seeded_product.id), "quantity": 1}], "payment_method": "cash", "cash_received": "200"},
    )

    # cajero NO puede listar
    r_cashier = client.get("/sales", headers=_auth(cashier))
    assert r_cashier.status_code == 403

    # admin SÍ
    r_admin = client.get("/sales", headers=_auth(admin))
    assert r_admin.status_code == 200
    assert len(r_admin.json()) == 1


def test_reports_daily_corte_del_dia(client, seeded_users, seeded_product):
    cashier = _login(client, "cashier@test.com", "cashpw")
    admin = _login(client, "admin@test.com", "adminpw")

    # 2 ventas hoy: una en efectivo, otra en transferencia
    pid = str(seeded_product.id)
    client.post(
        "/sales",
        headers=_auth(cashier),
        json={"items": [{"product_id": pid, "quantity": 1}], "payment_method": "cash", "cash_received": "200"},
    )
    client.post(
        "/sales",
        headers=_auth(cashier),
        json={"items": [{"product_id": pid, "quantity": 2}], "payment_method": "transfer"},
    )

    report = client.get("/reports/daily", headers=_auth(admin))
    assert report.status_code == 200, report.text
    body = report.json()
    assert body["totals"]["tickets"] == 2
    assert set(body["by_payment_method"].keys()) == {"cash", "transfer"}
    assert body["by_payment_method"]["cash"]["count"] == 1
    assert body["by_payment_method"]["transfer"]["count"] == 1


def test_reports_daily_cajero_no_autorizado(client, seeded_users):
    cashier = _login(client, "cashier@test.com", "cashpw")
    r = client.get("/reports/daily", headers=_auth(cashier))
    assert r.status_code == 403
