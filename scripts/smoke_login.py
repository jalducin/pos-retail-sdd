"""Smoke test in-process: monta la app, prueba /auth/login con las credenciales
sembradas usando la DB sqlite local. No requiere uvicorn corriendo.

Uso: python -m scripts.smoke_login
"""
from fastapi.testclient import TestClient

from app.main import app


def main() -> None:
    client = TestClient(app)
    cases = [
        ("admin@pos.com", "admin123", 200, "admin"),
        ("cajero@pos.com", "cajero123", 200, "cashier"),
        ("admin@pos.com", "wrong-pw", 401, None),
        ("nadie@pos.com", "x", 401, None),
    ]
    ok = True
    for email, password, expected, role in cases:
        r = client.post("/auth/login", json={"email": email, "password": password})
        passed = r.status_code == expected
        ok &= passed
        marker = "OK " if passed else "FAIL"
        print(f"[{marker}] {email:25s} pw={password:10s} -> {r.status_code} (expected {expected})")
        if r.status_code == 200 and role:
            from jose import jwt as jose_jwt

            from app.core.config import get_settings

            s = get_settings()
            payload = jose_jwt.decode(r.json()["access_token"], s.jwt_secret, algorithms=[s.jwt_algorithm])
            assert payload["role"] == role, f"role esperado {role}, recibido {payload['role']}"
            print(f"      role={payload['role']} sub={payload['sub']}")

    if not ok:
        raise SystemExit(1)
    print("\nLogin smoke OK.")


if __name__ == "__main__":
    main()
