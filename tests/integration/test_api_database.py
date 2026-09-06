import logging
import os

import httpx
import psycopg
import pytest


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/burn_calories_test",
)
LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def client():
    LOGGER.info("Creating API client for %s", API_BASE_URL)
    with httpx.Client(base_url=API_BASE_URL, timeout=10) as api_client:
        yield api_client
    LOGGER.info("API client closed")


def query_count(table_name: str) -> int:
    with psycopg.connect(TEST_DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            LOGGER.info("Database table %s contains %d rows", table_name, count)
            return count


def test_activities_are_seeded_from_postgres(client):
    LOGGER.info("Checking seeded activities through the API")
    response = client.get("/api/activities")
    LOGGER.info("GET /api/activities returned HTTP %d", response.status_code)

    assert response.status_code == 200
    activities = response.json()
    LOGGER.info("Received %d activities", len(activities))
    assert {activity["name"] for activity in activities} >= {
        "running",
        "walking",
        "cycling",
    }


def test_create_workout_persists_calculated_row(client):
    LOGGER.info("Creating a running workout and verifying PostgreSQL persistence")
    before = query_count("workout_entries")

    response = client.post(
        "/api/workouts",
        json={"activity": "running", "durationMinutes": 30, "weightKg": 70},
    )
    LOGGER.info("POST /api/workouts returned HTTP %d: %s", response.status_code, response.json())

    assert response.status_code == 201
    workout = response.json()
    assert workout["activity"] == "running"
    assert workout["caloriesBurned"] == pytest.approx(360.15)
    after = query_count("workout_entries")
    LOGGER.info("Workout row count changed from %d to %d", before, after)
    assert after == before + 1


def test_exercise_needed_calculation_persists_row(client):
    LOGGER.info("Creating an exercise-needed calculation and verifying persistence")
    before = query_count("exercise_needed_entries")

    response = client.post(
        "/api/exercise-needed",
        json={"activity": "cycling", "caloriesConsumed": 500, "weightKg": 70},
    )
    LOGGER.info("POST /api/exercise-needed returned HTTP %d: %s", response.status_code, response.json())

    assert response.status_code == 201
    calculation = response.json()
    assert calculation["activity"] == "cycling"
    assert calculation["durationMinutes"] == pytest.approx(54.42)
    after = query_count("exercise_needed_entries")
    LOGGER.info("Exercise-needed row count changed from %d to %d", before, after)
    assert after == before + 1

    history_response = client.get("/api/exercise-needed")
    LOGGER.info("GET /api/exercise-needed returned HTTP %d", history_response.status_code)
    assert history_response.status_code == 200
    assert any(item["id"] == calculation["id"] for item in history_response.json())


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        (
            "/api/workouts",
            {"activity": "not-an-activity", "durationMinutes": 30, "weightKg": 70},
        ),
        (
            "/api/exercise-needed",
            {"activity": "running", "caloriesConsumed": 0, "weightKg": 70},
        ),
    ],
)
def test_invalid_requests_do_not_create_database_rows(client, path, payload):
    LOGGER.info("Checking rejected request: %s %s", path, payload)
    table_name = "workout_entries" if path == "/api/workouts" else "exercise_needed_entries"
    before = query_count(table_name)

    response = client.post(path, json=payload)
    LOGGER.info("POST %s returned HTTP %d: %s", path, response.status_code, response.json())

    assert response.status_code in (400, 422)
    after = query_count(table_name)
    LOGGER.info("Rejected request left %s row count unchanged at %d", table_name, after)
    assert after == before
