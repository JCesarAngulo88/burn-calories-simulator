from sqlalchemy import Column, Float, Integer, String, DateTime
from sqlalchemy.sql import func

from .database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    met_value = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class WorkoutEntry(Base):
    __tablename__ = "workout_entries"

    id = Column(Integer, primary_key=True, index=True)
    activity = Column(String, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    weight_kg = Column(Float, nullable=False)
    calories_burned = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ExerciseNeededEntry(Base):
    __tablename__ = "exercise_needed_entries"

    id = Column(Integer, primary_key=True, index=True)
    activity = Column(String, nullable=False)
    calories_consumed = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    duration_minutes = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    activity_preferred = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
