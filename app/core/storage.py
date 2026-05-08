from datetime import UTC, datetime
from math import ceil, log2
from threading import Lock
from uuid import UUID, uuid4

from fastapi import HTTPException, status

from app.core.schemas import (
    Category,
    CategoryCreate,
    CompetitionFormat,
    Draw,
    Match,
    MatchScheduleUpdate,
    MatchScoreCreate,
    MatchStatus,
    Registration,
    RegistrationCreate,
    RegistrationStatus,
    Tournament,
    TournamentCreate,
    TournamentStatus,
    TournamentUpdate,
)


class InMemoryStore:
    """Small in-memory store used by the MVP and tests.

    The API is intentionally repository-like so it can be replaced by
    SQLAlchemy/PostgreSQL without changing router contracts.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self.reset()

    def reset(self) -> None:
        with getattr(self, "_lock", Lock()):
            self.tournaments: dict[UUID, Tournament] = {}
            self.categories: dict[UUID, Category] = {}
            self.registrations: dict[UUID, Registration] = {}
            self.draws: dict[UUID, Draw] = {}
            self.matches: dict[UUID, Match] = {}

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC)

    def create_tournament(self, payload: TournamentCreate) -> Tournament:
        with self._lock:
            if any(t.slug == payload.slug for t in self.tournaments.values()):
                raise HTTPException(status.HTTP_409_CONFLICT, "Tournament slug already exists")
            tournament = Tournament(id=uuid4(), created_at=self._now(), **payload.model_dump())
            self.tournaments[tournament.id] = tournament
            return tournament

    def list_tournaments(self) -> list[Tournament]:
        return sorted(self.tournaments.values(), key=lambda item: item.created_at)

    def get_tournament(self, tournament_id: UUID) -> Tournament:
        tournament = self.tournaments.get(tournament_id)
        if tournament is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Tournament not found")
        return tournament

    def get_public_tournament(self, slug: str) -> Tournament:
        for tournament in self.tournaments.values():
            if tournament.slug == slug and tournament.is_public:
                return tournament
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Published tournament not found")

    def update_tournament(self, tournament_id: UUID, payload: TournamentUpdate) -> Tournament:
        with self._lock:
            tournament = self.get_tournament(tournament_id)
            update = payload.model_dump(exclude_unset=True)
            updated = tournament.model_copy(update=update)
            self.tournaments[tournament_id] = updated
            return updated

    def set_tournament_status(self, tournament_id: UUID, new_status: TournamentStatus) -> Tournament:
        with self._lock:
            tournament = self.get_tournament(tournament_id)
            updated = tournament.model_copy(update={"status": new_status})
            self.tournaments[tournament_id] = updated
            return updated

    def create_category(self, tournament_id: UUID, payload: CategoryCreate) -> Category:
        self.get_tournament(tournament_id)
        if payload.max_participants < payload.min_participants:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "max_participants must be at least min_participants")
        with self._lock:
            category = Category(id=uuid4(), tournament_id=tournament_id, created_at=self._now(), **payload.model_dump())
            self.categories[category.id] = category
            return category

    def get_category(self, category_id: UUID) -> Category:
        category = self.categories.get(category_id)
        if category is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
        return category

    def list_categories(self, tournament_id: UUID) -> list[Category]:
        self.get_tournament(tournament_id)
        return [category for category in self.categories.values() if category.tournament_id == tournament_id]

    def create_registration(self, category_id: UUID, payload: RegistrationCreate) -> Registration:
        category = self.get_category(category_id)
        if category.modality == "singles" and len(payload.player_names) != 1:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Singles registrations require exactly one player")
        if category.modality == "doubles" and len(payload.player_names) != 2:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Doubles registrations require exactly two players")
        existing = [registration for registration in self.registrations.values() if registration.category_id == category_id]
        if len(existing) >= category.max_participants:
            default_status = RegistrationStatus.WAITLISTED
        else:
            default_status = RegistrationStatus.PENDING
        with self._lock:
            registration = Registration(
                id=uuid4(),
                category_id=category_id,
                status=default_status,
                created_at=self._now(),
                **payload.model_dump(),
            )
            self.registrations[registration.id] = registration
            return registration

    def list_registrations(self, category_id: UUID) -> list[Registration]:
        self.get_category(category_id)
        return [registration for registration in self.registrations.values() if registration.category_id == category_id]

    def get_registration(self, registration_id: UUID) -> Registration:
        registration = self.registrations.get(registration_id)
        if registration is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Registration not found")
        return registration

    def set_registration_status(self, registration_id: UUID, new_status: RegistrationStatus) -> Registration:
        with self._lock:
            registration = self.get_registration(registration_id)
            updated = registration.model_copy(update={"status": new_status})
            self.registrations[registration_id] = updated
            return updated

    def generate_draw(self, category_id: UUID) -> Draw:
        category = self.get_category(category_id)
        if category.format != CompetitionFormat.SINGLE_ELIMINATION:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Only single elimination draw generation is implemented")
        confirmed = [
            registration
            for registration in self.list_registrations(category_id)
            if registration.status == RegistrationStatus.CONFIRMED
        ]
        if len(confirmed) < category.min_participants:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Not enough confirmed registrations to generate draw")
        bracket_size = 2 ** ceil(log2(len(confirmed)))
        slots: list[Registration | None] = confirmed + [None] * (bracket_size - len(confirmed))
        draw_id = uuid4()
        matches: list[Match] = []
        for index in range(0, bracket_size, 2):
            home = slots[index]
            away = slots[index + 1]
            winner_id = home.id if home and away is None else None
            match_status = MatchStatus.FINISHED if winner_id else MatchStatus.SCHEDULED
            matches.append(
                Match(
                    id=uuid4(),
                    category_id=category_id,
                    draw_id=draw_id,
                    round_number=1,
                    order=(index // 2) + 1,
                    home_registration_id=home.id if home else None,
                    away_registration_id=away.id if away else None,
                    winner_registration_id=winner_id,
                    status=match_status,
                    created_at=self._now(),
                )
            )
        with self._lock:
            for match in matches:
                self.matches[match.id] = match
            draw = Draw(
                id=draw_id,
                category_id=category_id,
                format=category.format,
                generated_at=self._now(),
                match_ids=[match.id for match in matches],
            )
            self.draws[draw.id] = draw
            return draw

    def get_draws_for_category(self, category_id: UUID) -> list[Draw]:
        self.get_category(category_id)
        return [draw for draw in self.draws.values() if draw.category_id == category_id]

    def list_matches_for_category(self, category_id: UUID) -> list[Match]:
        self.get_category(category_id)
        return [match for match in self.matches.values() if match.category_id == category_id]

    def get_match(self, match_id: UUID) -> Match:
        match = self.matches.get(match_id)
        if match is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Match not found")
        return match

    def schedule_match(self, match_id: UUID, payload: MatchScheduleUpdate) -> Match:
        with self._lock:
            match = self.get_match(match_id)
            for existing in self.matches.values():
                if existing.id == match_id or existing.starts_at != payload.starts_at:
                    continue
                if existing.court == payload.court:
                    raise HTTPException(status.HTTP_409_CONFLICT, "Court is already booked at this time")
                existing_players = {existing.home_registration_id, existing.away_registration_id} - {None}
                match_players = {match.home_registration_id, match.away_registration_id} - {None}
                if existing_players & match_players:
                    raise HTTPException(status.HTTP_409_CONFLICT, "Player already has a match at this time")
            updated = match.model_copy(update={"court": payload.court, "starts_at": payload.starts_at})
            self.matches[match_id] = updated
            return updated

    def record_score(self, match_id: UUID, payload: MatchScoreCreate) -> Match:
        with self._lock:
            match = self.get_match(match_id)
            competitors = {match.home_registration_id, match.away_registration_id} - {None}
            if payload.winner_registration_id not in competitors:
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Winner must be one of the match registrations")
            updated = match.model_copy(
                update={
                    "score": payload.sets,
                    "winner_registration_id": payload.winner_registration_id,
                    "status": MatchStatus.FINISHED,
                }
            )
            self.matches[match_id] = updated
            return updated


store = InMemoryStore()
