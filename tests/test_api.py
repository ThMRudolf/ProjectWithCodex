from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.core.storage import store
from app.main import app


@pytest.fixture(autouse=True)
def clean_store():
    store.reset()
    yield
    store.reset()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def create_tournament(client: TestClient) -> dict:
    response = client.post(
        "/tournaments",
        json={
            "name": "Open Primavera",
            "slug": "open-primavera",
            "venue": "Club Central",
            "surface": "clay",
        },
    )
    assert response.status_code == 201
    return response.json()


def create_category(client: TestClient, tournament_id: str) -> dict:
    response = client.post(
        f"/tournaments/{tournament_id}/categories",
        json={"name": "Singles A", "modality": "singles", "min_participants": 2, "max_participants": 8},
    )
    assert response.status_code == 201
    return response.json()


def create_registration(client: TestClient, category_id: str, player_name: str) -> dict:
    response = client.post(
        f"/categories/{category_id}/registrations",
        json={"player_names": [player_name], "contact_email": f"{player_name.lower()}@example.com"},
    )
    assert response.status_code == 201
    registration = response.json()
    status_response = client.patch(
        f"/registrations/{registration['id']}/status",
        json={"status": "confirmed"},
    )
    assert status_response.status_code == 200
    return status_response.json()


def test_health_check(client: TestClient):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"message": "ok"}


def test_tournament_category_registration_and_public_flow(client: TestClient):
    tournament = create_tournament(client)
    category = create_category(client, tournament["id"])
    registration = create_registration(client, category["id"], "Nadal")

    registrations_response = client.get(f"/categories/{category['id']}/registrations")
    assert registrations_response.status_code == 200
    assert registrations_response.json()[0]["id"] == registration["id"]

    publish_response = client.post(f"/tournaments/{tournament['id']}/publish")
    assert publish_response.status_code == 200
    assert publish_response.json()["is_public"] is True

    public_response = client.get("/public/tournaments/open-primavera")
    assert public_response.status_code == 200
    assert public_response.json()["slug"] == "open-primavera"


def test_generates_single_elimination_draw_and_records_score(client: TestClient):
    tournament = create_tournament(client)
    category = create_category(client, tournament["id"])
    player_one = create_registration(client, category["id"], "Serena")
    player_two = create_registration(client, category["id"], "Venus")

    draw_response = client.post(f"/categories/{category['id']}/draws/generate")
    assert draw_response.status_code == 201
    draw = draw_response.json()
    assert len(draw["match_ids"]) == 1

    starts_at = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    schedule_response = client.patch(
        f"/matches/{draw['match_ids'][0]}/schedule",
        json={"court": "Court 1", "starts_at": starts_at},
    )
    assert schedule_response.status_code == 200
    assert schedule_response.json()["court"] == "Court 1"

    score_response = client.post(
        f"/matches/{draw['match_ids'][0]}/score",
        json={
            "sets": [{"home_games": 6, "away_games": 4}, {"home_games": 6, "away_games": 3}],
            "winner_registration_id": player_one["id"],
        },
    )
    assert score_response.status_code == 200
    assert score_response.json()["status"] == "finished"
    assert score_response.json()["winner_registration_id"] == player_one["id"]
    assert player_two["id"] in {
        score_response.json()["home_registration_id"],
        score_response.json()["away_registration_id"],
    }


def test_rejects_draw_when_not_enough_confirmed_players(client: TestClient):
    tournament = create_tournament(client)
    category = create_category(client, tournament["id"])
    create_registration(client, category["id"], "Alcaraz")

    response = client.post(f"/categories/{category['id']}/draws/generate")

    assert response.status_code == 422
    assert response.json()["detail"] == "Not enough confirmed registrations to generate draw"


def test_cors_preflight_allows_configured_frontend_origin(client: TestClient):
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "GET" in response.headers["access-control-allow-methods"]
