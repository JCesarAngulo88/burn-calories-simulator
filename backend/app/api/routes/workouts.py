from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import WorkoutEntry
from ...schemas import WorkoutInput, WorkoutResponse
from ...services.calorie_service import calculate_calories

router = APIRouter()


def serialize_workout(entry: WorkoutEntry) -> dict:
    return {"id": entry.id, "activity": entry.activity, "durationMinutes": entry.duration_minutes,
            "weightKg": entry.weight_kg, "caloriesBurned": entry.calories_burned, "createdAt": entry.created_at}


def find_workout(workout_id: int, db: Session) -> WorkoutEntry:
    entry = db.query(WorkoutEntry).filter(WorkoutEntry.id == workout_id).first()
    if entry is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return entry


@router.post("", response_model=WorkoutResponse, status_code=201)
def create_workout(payload: WorkoutInput, db: Session = Depends(get_db)):
    entry = WorkoutEntry(activity=payload.activity, duration_minutes=payload.durationMinutes,
                         weight_kg=payload.weightKg,
                         calories_burned=calculate_calories(payload.activity, payload.durationMinutes, payload.weightKg))
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return serialize_workout(entry)


@router.get("", response_model=list[WorkoutResponse])
def list_workouts(db: Session = Depends(get_db)):
    entries = db.query(WorkoutEntry).order_by(WorkoutEntry.created_at.desc()).all()
    return [serialize_workout(entry) for entry in entries]


@router.get("/{workout_id}", response_model=WorkoutResponse)
def get_workout(workout_id: int, db: Session = Depends(get_db)):
    return serialize_workout(find_workout(workout_id, db))


@router.put("/{workout_id}", response_model=WorkoutResponse)
def update_workout(workout_id: int, payload: WorkoutInput, db: Session = Depends(get_db)):
    entry = find_workout(workout_id, db)
    entry.activity = payload.activity
    entry.duration_minutes = payload.durationMinutes
    entry.weight_kg = payload.weightKg
    entry.calories_burned = calculate_calories(payload.activity, payload.durationMinutes, payload.weightKg)
    db.commit()
    db.refresh(entry)
    return serialize_workout(entry)


@router.delete("/{workout_id}", status_code=204)
def delete_workout(workout_id: int, db: Session = Depends(get_db)):
    db.delete(find_workout(workout_id, db))
    db.commit()
    return Response(status_code=204)