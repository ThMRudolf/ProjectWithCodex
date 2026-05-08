# ProjectWithCodex

Backend FastAPI para administrar torneos de tenis: torneos, categorías, inscripciones, cuadros, programación de partidos, resultados y endpoints públicos.

## Requisitos

- Python 3.12 o superior
- FastAPI
- Uvicorn

## Configuración

El backend habilita CORS para orígenes locales de desarrollo por defecto:

- `http://localhost:3000`
- `http://localhost:5173`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`

Puedes sobrescribirlos con una lista separada por comas en la variable de entorno `BACKEND_CORS_ORIGINS`.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Ejecutar la API

```bash
uvicorn app.main:app --reload
```

La documentación interactiva queda disponible en:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## Endpoints principales

- `GET /health`
- `POST /tournaments`
- `GET /tournaments`
- `POST /tournaments/{tournament_id}/categories`
- `POST /categories/{category_id}/registrations`
- `POST /categories/{category_id}/draws/generate`
- `PATCH /matches/{match_id}/schedule`
- `POST /matches/{match_id}/score`
- `GET /public/tournaments/{slug}`

## Pruebas

```bash
pytest
```
