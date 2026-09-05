from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes.health import router as health_router
from .api.routes.users import router as users_router
from .api.routes.workouts import router as workouts_router
from .database import Base, engine
from .models import User, WorkoutEntry  # noqa: F401

app = FastAPI(title="Burn Calories Simulator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)
app.include_router(health_router)
app.include_router(workouts_router, prefix="/api/workouts", tags=["workouts"])
app.include_router(users_router, prefix="/api/users", tags=["users"])
