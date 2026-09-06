from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/burn_calories",
)

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DEFAULT_ACTIVITIES = {
    "running": 9.8,
    "walking": 3.5,
    "cycling": 7.5,
    "swimming": 8.3,
    "yoga": 2.5,
    "gym": 6.0,
}


def initialize_database():
    from .models import Activity

    Base.metadata.create_all(bind=engine)
    user_columns = {column["name"] for column in inspect(engine).get_columns("users")}
    if "activity_preferred" not in user_columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE users ADD COLUMN activity_preferred VARCHAR"))

    with SessionLocal() as db:
        for name, met_value in DEFAULT_ACTIVITIES.items():
            if not db.query(Activity).filter(Activity.name == name).first():
                db.add(Activity(name=name, met_value=met_value))
        db.commit()
