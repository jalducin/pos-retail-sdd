"""Listado rápido de tablas creadas por Alembic. Uso: python -m scripts.check_db"""
import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "pos_local.db"
con = sqlite3.connect(DB)
tables = sorted(r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
print(f"DB: {DB}")
print(f"Tablas ({len(tables)}): {tables}")
sys.exit(0)
