from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Activity
from ...schemas import ActivityInput, ActivityResponse

router = APIRouter()


def serialize_activity(activity: Activity) -> dict:
    return {"id": activity.id, "name": activity.name, "metValue": activity.met_value,
            "createdAt": activity.created_at}


@router.get("", response_model=list[ActivityResponse])
def list_activities(db: Session = Depends(get_db)):
    activities = db.query(Activity).order_by(Activity.name.asc()).all()
    return [serialize_activity(activity) for activity in activities]


@router.post("", response_model=ActivityResponse, status_code=201)
def create_activity(payload: ActivityInput, db: Session = Depends(get_db)):
    name = payload.name.strip()
    existing = db.query(Activity).filter(Activity.name.ilike(name)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Activity already exists")

    activity = Activity(name=name, met_value=payload.metValue)
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return serialize_activity(activity)