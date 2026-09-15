import logging

import pytest

from app.services.calorie_service import calculate_calories, calculate_duration_minutes

LOGGER = logging.getLogger(__name__)


@pytest.mark.parametrize(
    ("duration_minutes", "weight_kg", "met_value", "expected"),
    [
        (30, 70, 9.8, 360.15),
        (60, 70, 3.5, 257.25),
        (20, 80, 7.5, 210.0),
    ],
)
def test_calculate_calories_uses_met_weight_and_duration(
    duration_minutes, weight_kg, met_value, expected
):
    actual = calculate_calories("running", duration_minutes, weight_kg, met_value)
    LOGGER.info(
        "Calorie calculation: duration=%s min, weight=%s kg, MET=%s, result=%s kcal, expected=%s kcal",
        duration_minutes,
        weight_kg,
        met_value,
        actual,
        expected,
    )
    assert actual == expected


@pytest.mark.parametrize(
    ("calories", "weight_kg", "met_value", "expected"),
    [
        (500, 70, 7.5, 54.42),
        (360.15, 70, 9.8, 30.0),
        (210, 80, 7.5, 20.0),
    ],
)
def test_calculate_duration_minutes_is_inverse_of_calorie_calculation(
    calories, weight_kg, met_value, expected
):
    actual = calculate_duration_minutes(calories, weight_kg, met_value)
    LOGGER.info(
        "Duration calculation: calories=%s kcal, weight=%s kg, MET=%s, result=%s min, expected=%s min",
        calories,
        weight_kg,
        met_value,
        actual,
        expected,
    )
    assert actual == expected


def test_calculate_duration_minutes_rejects_zero_calories_per_minute():
    LOGGER.info("Checking duration calculation rejects a zero MET value")
    with pytest.raises(ZeroDivisionError):
        calculate_duration_minutes(500, 70, 0)
