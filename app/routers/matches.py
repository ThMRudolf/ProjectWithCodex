from uuid import UUID

from fastapi import APIRouter

from app.core.schemas import Match, MatchScheduleUpdate, MatchScoreCreate
from app.core.storage import store

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("/{match_id}", response_model=Match)
def get_match(match_id: UUID) -> Match:
    return store.get_match(match_id)


@router.patch("/{match_id}/schedule", response_model=Match)
def schedule_match(match_id: UUID, payload: MatchScheduleUpdate) -> Match:
    return store.schedule_match(match_id, payload)


@router.post("/{match_id}/score", response_model=Match)
def record_score(match_id: UUID, payload: MatchScoreCreate) -> Match:
    return store.record_score(match_id, payload)


@router.post("/{match_id}/confirm-result", response_model=Match)
def confirm_result(match_id: UUID) -> Match:
    return store.get_match(match_id)
