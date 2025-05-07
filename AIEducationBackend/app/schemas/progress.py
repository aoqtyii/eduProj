# app/schemas/progress.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProgressBase(BaseModel):
    lesson_id: int
    completed: Optional[bool] = False
    score: Optional[float] = None


class ProgressCreate(ProgressBase):
    # user_id will come from context (logged-in user)
    pass


class ProgressUpdate(BaseModel):
    # Allow updating completion status, score
    completed: Optional[bool] = None
    score: Optional[float] = None
    # last_accessed_at is usually updated automatically


# Schema for representing progress in DB (usually internal)
class ProgressInDBBase(ProgressBase):
    id: int
    user_id: int
    last_accessed_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Pydantic V2
        # orm_mode = True # Pydantic V1


# Schema to return to the client
class Progress(ProgressInDBBase):
    # Optionally include nested lesson info if needed
    # lesson_title: Optional[str] = None # Example
    pass
