# POS Retail — Demo SDD

Sistema de Punto de Venta (POS) demo construido con metodología **Spec-Driven Development**.

## Stack

- **Backend**: Python 3.12 + FastAPI + SQLite (sin ORM)
- **Frontend**: HTML + CSS + JS vainilla (sin frameworks ni build step)

## Quickstart

```bash
pip install fastapi uvicorn
uvicorn backend.main:app --reload
# Abrir http://localhost:8000
```

## Metodología (SDD / OpenSpec)

```
Notion (User Story) → openspec/specs/ → código → tests → archive
```

El spec vive en `openspec/specs/pos-venta/`:
- `spec.md` — QUÉ debe hacer el sistema (requisitos + escenarios)
- `design.md` — CÓMO: decisiones técnicas y trade-offs
- `tasks.md` — plan de implementación paso a paso

**Regla principal**: si necesitas cambiar el comportamiento, actualiza el spec primero, luego el código.

## Estructura

```
pos-retail-sdd/
  backend/          # FastAPI app
  frontend/         # SPA vainilla
  openspec/         # Artefactos SDD
    specs/pos-venta/
  docs/             # Estándares del proyecto
  ai-specs/         # Agentes y skills para IA
```

## Fuera de alcance (v1)

- Autenticación de cajeros
- Métodos de pago y cálculo de cambio
- Impresión física de ticket
- Devoluciones / cancelaciones
