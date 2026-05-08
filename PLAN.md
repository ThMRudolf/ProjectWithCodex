# Plan del backend para torneo de tenis con FastAPI

## Objetivo

Construir un backend con FastAPI para gestionar torneos de tenis desde la creación del torneo hasta la publicación de resultados. El sistema debe cubrir torneos, categorías, inscripciones, generación de cuadros, programación de partidos, registro de marcadores y consulta pública.

## Alcance del MVP

El MVP debe permitir:

- Crear, consultar, actualizar, publicar y cancelar torneos.
- Crear categorías por torneo.
- Registrar jugadores o parejas en una categoría.
- Cambiar el estado de una inscripción.
- Generar cuadros de eliminación directa con jugadores confirmados.
- Programar partidos por cancha, fecha y hora.
- Registrar resultados y definir ganadores.
- Consultar torneos publicados desde endpoints públicos.
- Ejecutar pruebas automatizadas de los flujos principales.

## Stack propuesto

- **Framework:** FastAPI.
- **Lenguaje:** Python 3.12 o superior.
- **Validación:** Pydantic.
- **Servidor ASGI:** Uvicorn.
- **Base de datos inicial:** almacenamiento en memoria para MVP y pruebas.
- **Base de datos futura:** PostgreSQL.
- **ORM futuro:** SQLAlchemy.
- **Migraciones futuras:** Alembic.
- **Pruebas:** Pytest y `fastapi.testclient`.

## Estructura sugerida

```text
app/
  main.py
  core/
    schemas.py
    storage.py
  routers/
    tournaments.py
    categories.py
    registrations.py
    matches.py
    public.py
tests/
  test_api.py
```

## Entidades principales

- **Tournament:** representa el torneo, su nombre, slug, sede, superficie, fechas, visibilidad y estado.
- **Category:** representa una categoría del torneo, modalidad y formato competitivo.
- **Registration:** representa una inscripción individual o de pareja.
- **Draw:** representa el cuadro generado para una categoría.
- **Match:** representa un partido, participantes, horario, cancha, marcador, estado y ganador.

## Endpoints principales

### Salud

- `GET /health`

### Torneos

- `GET /tournaments`
- `POST /tournaments`
- `GET /tournaments/{tournament_id}`
- `PATCH /tournaments/{tournament_id}`
- `POST /tournaments/{tournament_id}/publish`
- `POST /tournaments/{tournament_id}/cancel`

### Categorías

- `GET /tournaments/{tournament_id}/categories`
- `POST /tournaments/{tournament_id}/categories`

### Inscripciones

- `POST /categories/{category_id}/registrations`
- `GET /categories/{category_id}/registrations`
- `PATCH /registrations/{registration_id}/status`

### Cuadros y partidos

- `POST /categories/{category_id}/draws/generate`
- `GET /categories/{category_id}/draws`
- `GET /categories/{category_id}/matches`
- `GET /matches/{match_id}`
- `PATCH /matches/{match_id}/schedule`
- `POST /matches/{match_id}/score`
- `POST /matches/{match_id}/confirm-result`

### API pública

- `GET /public/tournaments/{slug}`
- `GET /public/tournaments/{slug}/categories`
- `GET /public/categories/{category_id}/matches`

## Reglas de negocio iniciales

- Un slug de torneo no puede repetirse.
- Una categoría no puede generar cuadro si no tiene suficientes inscripciones confirmadas.
- Singles requiere exactamente un jugador por inscripción.
- Dobles requiere exactamente dos jugadores por inscripción.
- Si una categoría llega al cupo máximo, las nuevas inscripciones deben quedar en lista de espera.
- Una cancha no puede tener dos partidos en el mismo horario.
- Un jugador no puede tener dos partidos en el mismo horario.
- El ganador registrado debe pertenecer al partido.

## Fases de implementación

### Fase 1: API base

- Configurar proyecto FastAPI.
- Crear `pyproject.toml` con dependencias.
- Crear endpoint `GET /health`.
- Configurar CORS para permitir frontends locales de desarrollo.
- Crear esquemas Pydantic iniciales.
- Crear store en memoria para desarrollo y pruebas.

### Fase 2: Gestión del torneo

- Implementar endpoints de torneos.
- Implementar endpoints de categorías.
- Implementar endpoints de inscripciones.
- Implementar estados de torneo e inscripción.

### Fase 3: Competencia

- Implementar generación de cuadro de eliminación directa.
- Crear partidos automáticamente desde inscripciones confirmadas.
- Soportar byes básicos cuando el número de participantes no sea potencia de dos.

### Fase 4: Operación de partidos

- Implementar programación de partidos.
- Validar conflictos por cancha y jugador.
- Implementar carga de marcador.
- Confirmar ganador del partido.

### Fase 5: API pública y pruebas

- Exponer torneos publicados.
- Exponer categorías y partidos públicos.
- Agregar pruebas con `TestClient` para flujos principales.
- Documentar instalación, ejecución y pruebas en el README.

### Fase 6: Despliegue en Render

- Agregar `requirements.txt` para instalación de dependencias en Render.
- Agregar `.python-version` para fijar Python 3.12 en el servicio.
- Agregar `render.yaml` con build command, start command y health check.
- Configurar `BACKEND_CORS_ORIGINS` en Render con la URL del frontend de producción.
- Validar `/health` y `/docs` después del deploy.
## Criterios de aceptación

- La API inicia con `uvicorn app.main:app --reload`.
- `GET /health` responde `{"message": "ok"}`.
- Se puede crear un torneo y publicarlo.
- Se puede crear una categoría dentro de un torneo.
- Se pueden registrar jugadores y confirmar inscripciones.
- Se puede generar un cuadro con inscripciones confirmadas.
- Se puede programar un partido y registrar su resultado.
- Los endpoints públicos solo exponen torneos publicados.
- Las pruebas automatizadas cubren los flujos principales.
- Render despliega el servicio usando `render.yaml` y el endpoint `/health` responde correctamente.
