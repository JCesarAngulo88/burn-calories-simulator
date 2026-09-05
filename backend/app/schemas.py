from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WorkoutInput(BaseModel):
    activity: str = Field(min_length=1)
    durationMinutes: int = Field(gt=0)
    weightKg: float = Field(gt=0)


class WorkoutResponse(WorkoutInput):
    model_config = ConfigDict(from_attributes=True)

    id: int
    caloriesBurned: float
    createdAt: datetime


class UserInput(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(gt=0)
    email: str = Field(min_length=3)
    weightKg: float | None = Field(default=None, gt=0)
    heightCm: float | None = Field(default=None, gt=0)


class UserResponse(UserInput):
    model_config = ConfigDict(from_attributes=True)

    id: int
    createdAt: datetime