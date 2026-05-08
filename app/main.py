from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.schemas import Message
from app.routers import categories, matches, public, registrations, tournaments


def create_app() -> FastAPI:
    app = FastAPI(
        title="Tennis Tournament Backend",
        version="0.1.0",
        description="FastAPI backend for managing tennis tournaments, registrations, draws, schedules, and results.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
    app.include_router(tournaments.router)
    app.include_router(categories.router)
    app.include_router(matches.router)
    app.include_router(registrations.router)
    app.include_router(public.router)
    return app


app = create_app()


@app.get("/health", response_model=Message, tags=["health"])
def health_check() -> Message:
    return Message(message="ok")
