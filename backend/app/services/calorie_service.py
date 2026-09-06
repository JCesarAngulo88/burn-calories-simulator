def calculate_calories(activity: str, duration_minutes: int, weight_kg: float, met_value: float) -> float:
    met = met_value
    return round((met * 3.5 * weight_kg / 200) * duration_minutes, 2)