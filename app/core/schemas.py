from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TournamentStatus(StrEnum):
    DRAFT = "draft"
    REGISTRATION_OPEN = "registration_open"
    REGISTRATION_CLOSED = "registration_closed"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class RegistrationStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    WAITLISTED = "waitlisted"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class CompetitionFormat(StrEnum):
    SINGLE_ELIMINATION = "single_elimination"
    ROUND_ROBIN = "round_robin"


class MatchStatus(StrEnum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    WALKOVER = "walkover"
    RETIRED = "retired"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class Message(BaseModel):
    message: str


class TournamentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(min_length=1, max_length=140)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    venue: str | None = Field(default=None, max_length=160)
    surface: str | None = Field(default=None, max_length=80)
    is_public: bool = False


class TournamentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    venue: str | None = Field(default=None, max_length=160)
    surface: str | None = Field(default=None, max_length=80)
    is_public: bool | None = None


class Tournament(TournamentCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: TournamentStatus = TournamentStatus.DRAFT
    created_at: datetime


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    modality: str = Field(default="singles", pattern="^(singles|doubles)$")
    format: CompetitionFormat = CompetitionFormat.SINGLE_ELIMINATION
    max_participants: int = Field(default=32, ge=2, le=256)
    min_participants: int = Field(default=2, ge=2, le=256)

    @field_validator("max_participants")
    @classmethod
    def validate_participant_limits(cls, value: int, info):
        min_participants = info.data.get("min_participants")
        if min_participants is not None and value < min_participants:
            raise ValueError("max_participants must be greater than or equal to min_participants")
        return value


class Category(CategoryCreate):
    id: UUID
    tournament_id: UUID
    created_at: datetime


class RegistrationCreate(BaseModel):
    player_names: list[str] = Field(min_length=1, max_length=2)
    contact_email: str | None = Field(default=None, max_length=160)

    @field_validator("player_names")
    @classmethod
    def validate_player_names(cls, value: list[str]) -> list[str]:
        cleaned = [name.strip() for name in value]
        if any(not name for name in cleaned):
            raise ValueError("player names cannot be blank")
        return cleaned


class RegistrationStatusUpdate(BaseModel):
    status: RegistrationStatus


class Registration(RegistrationCreate):
    id: UUID
    category_id: UUID
    status: RegistrationStatus = RegistrationStatus.PENDING
    created_at: datetime


class DrawGenerateRequest(BaseModel):
    seed_registration_ids: list[UUID] | None = None


class Draw(BaseModel):
    id: UUID
    category_id: UUID
    format: CompetitionFormat
    generated_at: datetime
    match_ids: list[UUID]


class MatchScheduleUpdate(BaseModel):
    court: str = Field(min_length=1, max_length=120)
    starts_at: datetime


class ScoreSet(BaseModel):
    home_games: int = Field(ge=0, le=99)
    away_games: int = Field(ge=0, le=99)


class MatchScoreCreate(BaseModel):
    sets: list[ScoreSet] = Field(min_length=1, max_length=5)
    winner_registration_id: UUID


class Match(BaseModel):
    id: UUID
    category_id: UUID
    draw_id: UUID | None = None
    round_number: int = Field(ge=1)
    order: int = Field(ge=1)
    home_registration_id: UUID | None = None
    away_registration_id: UUID | None = None
    court: str | None = None
    starts_at: datetime | None = None
    status: MatchStatus = MatchStatus.SCHEDULED
    winner_registration_id: UUID | None = None
    score: list[ScoreSet] = Field(default_factory=list)
    created_at: datetime
