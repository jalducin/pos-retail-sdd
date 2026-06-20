# Contexto del proyecto

## Qué es

Sistema de Punto de Venta (POS) demo para practicar Spec-Driven Development de punta a punta.
Permite a un cajero seleccionar productos de un catálogo, armar un ticket en tiempo real y
confirmar el cobro, descontando el stock de forma atómica en la base de datos.

## Stack tecnológico

- Lenguaje: Python 3.12
- Framework backend: FastAPI
- Base de datos: SQLite (driver nativo `sqlite3`, sin ORM)
- Frontend: HTML + CSS + JS vainilla (sin frameworks ni build step), servido por `StaticFiles`

## Arquitectura

Monolito ligero de 2 capas:
- `backend/` — FastAPI app: rutas, validación de negocio y acceso a datos en `main.py`; schema + seed en `database.py`.
- `frontend/` — SPA vainilla: estado del carrito en memoria, fetch a la API, render reactivo sin build step.

Sin ORM: con 3 tablas, SQL directo con `sqlite3.Row` es suficiente y más legible.

## Convenciones

- Idioma: documentación y comentarios en español; identificadores de código en inglés (convención Python/JS).
- Commits: conventional commits.
- Ramas: `feature/[change-name]`.
- Estándares en `docs/base-standards.md` y `docs/documentation-standards.md`.

## Comandos clave

- Instalar dependencias: `pip install fastapi uvicorn`
- Levantar el proyecto: `uvicorn backend.main:app --reload`
- Ejecutar pruebas: `pytest`
