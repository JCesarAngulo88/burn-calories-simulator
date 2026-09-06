from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Activity, ExerciseNeededEntry
from ...schemas import ExerciseNeededInput, ExerciseNeededResponse
from ...services.calorie_service import calculate_duration_minutes

router = APIRouter()


def serialize_entry(entry: ExerciseNeededEntry) -> dict:
    return {
        "id": entry.id,
        "activity": entry.activity,
        "caloriesConsumed": entry.calories_consumed,
        "weightKg": entry.weight_kg,
        "durationMinutes": entry.duration_minutes,
        "createdAt": entry.created_at,
    }


def find_activity(name: str, db: Session) -> Activity:
    activity = db.query(Activity).filter(Activity.name.ilike(name.strip())).first()
    if activity is None:
        raise HTTPException(status_code=400, detail="Activity is not available")
    return activity


@router.post("", response_model=ExerciseNeededResponse, status_code=201)
def create_exercise_needed(payload: ExerciseNeededInput, db: Session = Depends(get_db)):
    activity = find_activity(payload.activity, db)
    entry = ExerciseNeededEntry(
        activity=activity.name,
        calories_consumed=payload.caloriesConsumed,
        weight_kg=payload.weightKg,
        duration_minutes=calculate_duration_minutes(
            payload.caloriesConsumed, payload.weightKg, activity.met_value
        ),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return serialize_entry(entry)


@router.get("", response_model=list[ExerciseNeededResponse])
def list_exercise_needed(db: Session = Depends(get_db)):
    entries = db.query(ExerciseNeededEntry).order_by(ExerciseNeededEntry.created_at.desc()).all()
    return [serialize_entry(entry) for entry in entries]