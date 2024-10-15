import os
from dotenv import load_dotenv
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Annotated
from fastapi import Depends, HTTPException, Query, Path, Body, Form
from sqlalchemy.orm import Session
from mangum import Mangum

# Load environment variables from the .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Initialize the Mangum handler
handler = Mangum(app)

# SQLite setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Rest of your app code here...
Base = declarative_base()

# Database model for Workout
class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    workout_type = Column(String, index=True)
    distance = Column(Float)
    time = Column(Float)  # in minutes
    date = Column(DateTime, default=datetime.now())

# Pydantic model for input validation
class WorkoutCreate(BaseModel):
    workout_type: str = Field(..., example="running")
    distance: float = Field(..., example=5.0)  # in kilometers
    time: float = Field(..., example=30.0)  # in minutes
    date: datetime = Field(default_factory=datetime.now, example="2023-06-01T12:00:00")

# Create database tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# home page 
@app.get('/')
def welcome():
    return "Welcome to the Triathlon Training Tracker API page!"

# API to log a workout
@app.post("/workout")
def log_workout(workout: WorkoutCreate, db: Session = Depends(get_db)):
    # Validate workout type
    if workout.workout_type not in ["running", "swimming", "cycling"]:
        raise HTTPException(status_code=400, detail="Invalid workout type")
    
    # Create new workout instance
    db_workout = Workout(
        workout_type=workout.workout_type,
        distance=workout.distance,
        time=workout.time,
        date=workout.date
    )
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout

# API to get workout history
@app.get("/workouts")
def get_workout_history(db: Session = Depends(get_db)):
    workouts = db.query(Workout).all()
    return workouts

# API to delete a specified workout
@app.delete("/workout/{workout_id}")
def delete_workout(workout_id: int, db: Session = Depends(get_db)):
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    db.delete(workout)
    db.commit()
    return {"message": f"Workout with id {workout_id} has been deleted"}