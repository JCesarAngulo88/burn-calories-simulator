from datetime import datetime, timezone
import logging

import pytest
from pydantic import ValidationError

from app.schemas import (
    ActivityInput,
    ExerciseNeededInput,
    ExerciseNeededResponse,
    WorkoutInput,
)

LOGGER = logging.getLogger(__name__)


def test_workout_input_accepts_valid_payload():
    LOGGER.info("Validating a positive workout payload")
    workout = WorkoutInput(activity="running", durationMinutes=30, weightKg=70)

    assert workout.activity == "running"
    assert workout.durationMinutes == 30
    assert workout.weightKg == 70


@pytest.mark.parametrize(
    "payload",
    [
        {"activity": "", "durationMinutes": 30, "weightKg": 70},
        {"activity": "running", "durationMinutes": 0, "weightKg": 70},
        {"activity": "running", "durationMinutes": 30, "weightKg": 0},
    ],
)
def test_workout_input_rejects_invalid_values(payload):
    LOGGER.info("Validating rejected workout payload: %s", payload)
    with pytest.raises(ValidationError):
        WorkoutInput.model_validate(payload)


def test_exercise_needed_input_requires_positive_calories():
    LOGGER.info("Validating exercise-needed input rejects zero calories")
    with pytest.raises(ValidationError):
        ExerciseNeededInput(
            activity="cycling",
            caloriesConsumed=0,
            weightKg=70,
        )


def test_activity_input_enforces_met_value_range():
    LOGGER.info("Validating activity input rejects MET values above 30")
    with pytest.raises(ValidationError):
        ActivityInput(name="extreme activity", metValue=30.1)


def test_exercise_needed_response_serializes_database_style_attributes():
    LOGGER.info("Validating exercise-needed response fields from database-style data")
    response = ExerciseNeededResponse.model_validate(
        {
            "id": 1,
            "activity": "cycling",
            "caloriesConsumed": 500,
            "weightKg": 70,
            "durationMinutes": 54.42,
            "createdAt": datetime.now(timezone.utc),
        }
    )

    assert response.id == 1
    assert response.durationMinutes == 54.42
    LOGGER.info("Response parsed successfully: id=%s, duration=%s min", response.id, response.durationMinutes)