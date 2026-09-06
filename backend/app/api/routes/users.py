from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import User
from ...schemas import UserInput, UserResponse

router = APIRouter()


def serialize_user(user: User) -> dict:
    return {"id": user.id, "name": user.name, "age": user.age, "email": user.email,
            "weightKg": user.weight_kg, "heightCm": user.height_cm,
            "activityPreferred": user.activity_preferred, "createdAt": user.created_at}


@router.post("", response_model=UserResponse, status_code=201)
def create_user(payload: UserInput, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email is already registered")
    user = User(name=payload.name, age=payload.age, email=payload.email,
                weight_kg=payload.weightKg, height_cm=payload.heightCm,
                activity_preferred=payload.activityPreferred)
    db.add(user)
    db.commit()
    db.refresh(user)
    return serialize_user(user)


@router.get("", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [serialize_user(user) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return serialize_user(user)