from uuid import UUID

from fastapi import APIRouter

from app.core.schemas import Registration, RegistrationStatusUpdate
from app.core.storage import store

router = APIRouter(prefix="/registrations", tags=["registrations"])


@router.patch("/{registration_id}/status", response_model=Registration)
def update_registration_status(registration_id: UUID, payload: RegistrationStatusUpdate) -> Registration:
    return store.set_registration_status(registration_id, payload.status)
