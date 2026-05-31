"""Script one-shot: migra emails de .local a .com en la DB local.

Razón: Pydantic EmailStr rechaza dominios .local (RFC 6762 reservado) y bloquea login.
Ver DT-13.

Uso: python -m scripts.fix_email_domain
"""
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "pos_local.db"

if not DB.exists():
    print(f"DB no encontrada en {DB}. Corre primero alembic upgrade head + scripts.seed_dev.")
    raise SystemExit(1)

con = sqlite3.connect(DB)
cur = con.cursor()

before = cur.execute("SELECT email FROM users WHERE email LIKE '%@%.local'").fetchall()
print(f"Emails con dominio .local encontrados: {len(before)}")
for (email,) in before:
    new_email = email.rsplit(".local", 1)[0] + ".com"
    cur.execute("UPDATE users SET email = ? WHERE email = ?", (new_email, email))
    print(f"  {email} -> {new_email}")

con.commit()
con.close()
print("Listo. Login debe funcionar ahora con los emails actualizados.")
