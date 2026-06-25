_AUTH = ("admin", "adminpizzeria2026&")


def test_openapi_json_accesible(client):
    resp = client.get("/openapi.json", auth=_AUTH)
    assert resp.status_code == 200
    data = resp.json()
    assert "paths" in data
    assert "/api/menu/sizes" in data["paths"]
    assert "/api/orders" in data["paths"]


def test_swagger_docs_accesible(client):
    resp = client.get("/docs", auth=_AUTH)
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


def test_docs_sin_credenciales_retorna_401(client):
    resp = client.get("/docs")
    assert resp.status_code == 401


def test_openapi_json_sin_credenciales_retorna_401(client):
    resp = client.get("/openapi.json")
    assert resp.status_code == 401
