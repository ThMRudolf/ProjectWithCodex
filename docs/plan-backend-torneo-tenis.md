# Plan de backend para un torneo de tenis

## 1. Objetivo y alcance

Construir un backend con **FastAPI** para administrar torneos de tenis desde la inscripción hasta la publicación de resultados. El sistema debe permitir registrar jugadores, definir categorías, generar cuadros o ligas, programar partidos, cargar resultados, calcular avances y exponer información pública para jugadores, organizadores y espectadores.

### 1.1 Stack backend propuesto

- **Framework API:** FastAPI con Python 3.12 o superior.
- **Validación y contratos:** Pydantic para esquemas de request/response y documentación OpenAPI automática.
- **Base de datos:** PostgreSQL como base relacional principal.
- **ORM y migraciones:** SQLAlchemy para modelos/repositorios y Alembic para migraciones.
- **Servidor ASGI:** Uvicorn para desarrollo y despliegue detrás de un proxy o plataforma compatible.
- **Pruebas:** Pytest con cliente de pruebas de FastAPI para validar endpoints y reglas de negocio.
- **Estructura sugerida:** separar routers, schemas, modelos, servicios, repositorios y configuración para mantener el dominio del torneo desacoplado de la capa HTTP.

## 2. Roles principales

- **Administrador del sistema:** gestiona usuarios, permisos, configuración global y auditoría.
- **Organizador del torneo:** crea torneos, categorías, sedes, horarios, cuadros, partidos y resultados.
- **Árbitro o mesa de control:** registra marcadores, incidencias y confirmaciones de partido.
- **Jugador:** consulta calendario, rivales, resultados, ranking y estado de inscripción.
- **Público:** consulta torneos, cuadros, horarios y resultados publicados.

## 3. Módulos funcionales

### 3.1 Autenticación y autorización

- Registro e inicio de sesión por email y contraseña.
- Recuperación de contraseña.
- Tokens de sesión con expiración.
- Roles y permisos por torneo.
- Auditoría de acciones críticas, como modificación de resultados o eliminación de partidos.

### 3.2 Gestión de jugadores

- Perfil del jugador con nombre, email, teléfono, fecha de nacimiento, género, mano dominante y nivel.
- Validación de elegibilidad por categoría.
- Historial de torneos, partidos y resultados.
- Estado de inscripción: pendiente, confirmada, en lista de espera, cancelada o rechazada.

### 3.3 Gestión de torneos

- Creación de torneo con nombre, fechas, sede, superficie, reglas y visibilidad pública.
- Estados del torneo: borrador, inscripciones abiertas, inscripciones cerradas, en curso, finalizado y cancelado.
- Configuración de límite de participantes, modalidad y reglas de desempate.
- Publicación controlada de horarios, cuadros y resultados.

### 3.4 Categorías y modalidades

- Categorías por edad, nivel, género o formato abierto.
- Modalidades de singles y dobles.
- Restricciones por cupo, nivel mínimo/máximo y edad.
- Reglas específicas por categoría: sets, super tie-break, walkover, retiro y abandono.

### 3.5 Inscripciones

- Inscripción individual o por pareja.
- Validación de cupos y lista de espera.
- Confirmación manual por organizador.
- Opcional: integración futura con pagos.
- Notificaciones de confirmación, cambios de horario y resultados.

### 3.6 Generación de competencia

- Formatos soportados en una primera versión:
  - Eliminación directa.
  - Round robin por grupos.
  - Cuadro con cabezas de serie.
- Generación automática de partidos.
- Soporte para byes.
- Reordenamiento manual antes de publicar el cuadro.
- Avance automático de ganadores cuando se confirma un resultado.

### 3.7 Programación de partidos

- Gestión de sedes y canchas.
- Disponibilidad por cancha y franja horaria.
- Asignación de partido a cancha, fecha y hora.
- Detección de conflictos de horario para jugadores, parejas y canchas.
- Reprogramación con registro de motivo.

### 3.8 Resultados y estadísticas

- Carga de marcador por sets.
- Validación del marcador según reglas de la categoría.
- Estados de partido: programado, en juego, finalizado, walkover, retiro, suspendido y cancelado.
- Cálculo de ganador, avance de ronda y tabla de grupos.
- Estadísticas básicas: partidos jugados, ganados, perdidos, sets a favor/en contra y games a favor/en contra.

### 3.9 API pública

- Endpoints de solo lectura para torneos publicados.
- Consulta de categorías, cuadros, grupos, partidos, horarios y resultados.
- Respuestas optimizadas para web o app móvil.
- Cache para páginas públicas de alto tráfico.

### 3.10 Notificaciones

- Email para confirmaciones importantes.
- Preparar arquitectura para integrar SMS, WhatsApp o push notifications en el futuro.
- Plantillas de mensajes por evento: inscripción confirmada, partido programado, partido reprogramado y resultado confirmado.

## 4. Modelo de datos inicial

Entidades principales:

- **User:** cuenta de acceso, email, contraseña cifrada, estado y rol global.
- **PlayerProfile:** datos deportivos y personales del jugador.
- **Tournament:** configuración general, fechas, sede, reglas y estado.
- **TournamentRole:** relación entre usuarios y permisos dentro de un torneo.
- **Venue:** sede física del torneo.
- **Court:** cancha perteneciente a una sede.
- **Category:** categoría del torneo con modalidad y reglas.
- **Registration:** inscripción de jugador o pareja a una categoría.
- **Team:** participante competitivo; puede representar un jugador de singles o una pareja de dobles.
- **Draw:** estructura competitiva de una categoría.
- **Group:** grupo de round robin, si aplica.
- **Match:** partido, ronda, orden, participantes, cancha, fecha, estado y ganador.
- **MatchScore:** marcador por sets y metadatos de resultado.
- **Notification:** mensajes enviados o pendientes.
- **AuditLog:** trazabilidad de cambios críticos.

## 5. Endpoints REST sugeridos

Los endpoints se implementarían como routers de FastAPI, agrupados por dominio para facilitar versionado, documentación OpenAPI y pruebas por módulo.

### 5.1 Autenticación

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`
- `POST /auth/password-reset/request`
- `POST /auth/password-reset/confirm`

### 5.2 Torneos

- `GET /tournaments`
- `POST /tournaments`
- `GET /tournaments/{tournamentId}`
- `PATCH /tournaments/{tournamentId}`
- `POST /tournaments/{tournamentId}/publish`
- `POST /tournaments/{tournamentId}/cancel`

### 5.3 Categorías e inscripciones

- `GET /tournaments/{tournamentId}/categories`
- `POST /tournaments/{tournamentId}/categories`
- `PATCH /categories/{categoryId}`
- `POST /categories/{categoryId}/registrations`
- `GET /categories/{categoryId}/registrations`
- `PATCH /registrations/{registrationId}/status`

### 5.4 Cuadros, grupos y partidos

- `POST /categories/{categoryId}/draws/generate`
- `GET /categories/{categoryId}/draws`
- `PATCH /draws/{drawId}`
- `GET /categories/{categoryId}/matches`
- `PATCH /matches/{matchId}/schedule`
- `POST /matches/{matchId}/score`
- `POST /matches/{matchId}/confirm-result`

### 5.5 API pública

- `GET /public/tournaments/{slug}`
- `GET /public/tournaments/{slug}/categories`
- `GET /public/categories/{categoryId}/draw`
- `GET /public/categories/{categoryId}/matches`
- `GET /public/matches/{matchId}`

## 6. Reglas de negocio clave

- Un jugador no puede tener dos partidos programados en la misma franja horaria.
- Una cancha no puede tener más de un partido activo en el mismo horario.
- Una categoría no puede generar cuadro si tiene menos participantes que el mínimo definido.
- Un resultado confirmado debe avanzar automáticamente al ganador en eliminación directa.
- Todo cambio manual de resultado confirmado debe crear un registro de auditoría.
- En dobles, una pareja debe tener exactamente dos jugadores activos.
- Los cuadros publicados no deben cambiarse sin registrar motivo y autor.

## 10. Estrategia de pruebas

- Pruebas unitarias para reglas de marcador, avance de rondas y desempates.
- Pruebas de integración para endpoints críticos.
- Pruebas de concurrencia para inscripciones y asignación de canchas.
- Pruebas end-to-end para flujo completo: crear torneo, inscribir jugadores, generar cuadro, programar partido y confirmar resultado.
- Pruebas de autorización por rol.

## 11. Roadmap recomendado

### Fase 1: MVP administrativo

- Autenticación básica.
- CRUD de torneos, categorías, jugadores e inscripciones.
- Generación de eliminación directa.
- Programación manual de partidos.
- Carga y confirmación de resultados.
- API pública de consulta.

### Fase 2: Operación de torneo

- Round robin por grupos.
- Validación avanzada de horarios.
- Notificaciones por email.
- Auditoría completa.
- Cache para vistas públicas.

### Fase 3: Escalabilidad y producto

- Pagos de inscripción.
- Rankings y estadísticas históricas.
- App móvil o soporte push.
- Importación masiva de jugadores.
- Panel analítico para organizadores.

## 12. Decisiones pendientes

- Reglas oficiales de desempate por formato.
- Si habrá pagos desde el MVP.
- Si el sistema será multi-club o solo para un organizador.
- Nivel de información pública permitida para perfiles de jugadores.
- Soporte requerido para zonas horarias si el producto se usa fuera de una sola región.
