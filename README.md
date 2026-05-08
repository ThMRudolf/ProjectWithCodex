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

## Despliegue en Render

Este repositorio incluye `render.yaml`, `requirements.txt` y `.python-version` para levantar el backend como un Web Service de Render.

### Opción recomendada: Blueprint

1. Sube este repositorio a GitHub, GitLab o Bitbucket.
2. En Render, crea un nuevo Blueprint y selecciona el repositorio.
3. Render detectará `render.yaml` en la raíz del proyecto.
4. Confirma la creación del servicio `tennis-tournament-backend`.
5. Cuando termine el deploy, valida:
   - `https://TU-SERVICIO.onrender.com/health`
   - `https://TU-SERVICIO.onrender.com/docs`

### Opción manual: Web Service

Si prefieres crear el servicio manualmente, usa estos valores:

- **Runtime:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path:** `/health`

### CORS en producción

Cuando tengas la URL del frontend, configura en Render la variable de entorno `BACKEND_CORS_ORIGINS` con los orígenes permitidos separados por comas. Ejemplo:

```text
https://mi-frontend.onrender.com,https://www.mi-dominio.com
```

Después de cambiar esa variable, redeploya el servicio para que FastAPI cargue la nueva configuración.

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
