from uuid import UUID

from fastapi import APIRouter, status

from app.core.schemas import (
    Category,
    CategoryCreate,
    Tournament,
    TournamentCreate,
    TournamentStatus,
    TournamentUpdate,
)
from app.core.storage import store

router = APIRouter(prefix="/tournaments", tags=["tournaments"])


@router.get("", response_model=list[Tournament])
def list_tournaments() -> list[Tournament]:
    return store.list_tournaments()


@router.post("", response_model=Tournament, status_code=status.HTTP_201_CREATED)
def create_tournament(payload: TournamentCreate) -> Tournament:
    return store.create_tournament(payload)


@router.get("/{tournament_id}", response_model=Tournament)
def get_tournament(tournament_id: UUID) -> Tournament:
    return store.get_tournament(tournament_id)


@router.patch("/{tournament_id}", response_model=Tournament)
def update_tournament(tournament_id: UUID, payload: TournamentUpdate) -> Tournament:
    return store.update_tournament(tournament_id, payload)


@router.post("/{tournament_id}/publish", response_model=Tournament)
def publish_tournament(tournament_id: UUID) -> Tournament:
    store.update_tournament(tournament_id, TournamentUpdate(is_public=True))
    return store.set_tournament_status(tournament_id, TournamentStatus.REGISTRATION_OPEN)


@router.post("/{tournament_id}/cancel", response_model=Tournament)
def cancel_tournament(tournament_id: UUID) -> Tournament:
    return store.set_tournament_status(tournament_id, TournamentStatus.CANCELLED)


@router.get("/{tournament_id}/categories", response_model=list[Category])
def list_categories(tournament_id: UUID) -> list[Category]:
    return store.list_categories(tournament_id)


@router.post("/{tournament_id}/categories", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(tournament_id: UUID, payload: CategoryCreate) -> Category:
    return store.create_category(tournament_id, payload)
