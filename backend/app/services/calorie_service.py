MET_VALUES = {"running": 9.8, "walking": 3.5, "cycling": 7.5, "swimming": 8.3, "yoga": 2.5, "gym": 6.0}


def calculate_calories(activity: str, duration_minutes: int, weight_kg: float) -> float:
    met = MET_VALUES.get(activity.lower(), 5.0)
    return round((met * 3.5 * weight_kg / 200) * duration_minutes, 2)