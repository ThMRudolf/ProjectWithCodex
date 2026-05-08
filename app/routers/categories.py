from uuid import UUID

from fastapi import APIRouter, status

from app.core.schemas import Draw, Match, Registration, RegistrationCreate
from app.core.storage import store

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/{category_id}/registrations", response_model=Registration, status_code=status.HTTP_201_CREATED)
def create_registration(category_id: UUID, payload: RegistrationCreate) -> Registration:
    return store.create_registration(category_id, payload)


@router.get("/{category_id}/registrations", response_model=list[Registration])
def list_registrations(category_id: UUID) -> list[Registration]:
    return store.list_registrations(category_id)


@router.post("/{category_id}/draws/generate", response_model=Draw, status_code=status.HTTP_201_CREATED)
def generate_draw(category_id: UUID) -> Draw:
    return store.generate_draw(category_id)


@router.get("/{category_id}/draws", response_model=list[Draw])
def list_draws(category_id: UUID) -> list[Draw]:
    return store.get_draws_for_category(category_id)


@router.get("/{category_id}/matches", response_model=list[Match])
def list_matches(category_id: UUID) -> list[Match]:
    return store.list_matches_for_category(category_id)
