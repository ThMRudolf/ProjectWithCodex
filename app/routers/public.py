from uuid import UUID

from fastapi import APIRouter

from app.core.schemas import Category, Match, Tournament
from app.core.storage import store

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/tournaments/{slug}", response_model=Tournament)
def get_public_tournament(slug: str) -> Tournament:
    return store.get_public_tournament(slug)


@router.get("/tournaments/{slug}/categories", response_model=list[Category])
def list_public_categories(slug: str) -> list[Category]:
    tournament = store.get_public_tournament(slug)
    return store.list_categories(tournament.id)


@router.get("/categories/{category_id}/matches", response_model=list[Match])
def list_public_matches(category_id: UUID) -> list[Match]:
    category = store.get_category(category_id)
    tournament = store.get_tournament(category.tournament_id)
    store.get_public_tournament(tournament.slug)
    return store.list_matches_for_category(category_id)
