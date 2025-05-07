# app/schemas/lesson.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LessonBase(BaseModel):
    title: str = Field(..., min_length=1)
    content: Optional[str] = None
    order: Optional[int] = 0


class LessonCreate(LessonBase):
    course_id: int  # Must specify course when creating


class LessonUpdate(LessonBase):
    # Allow updating title, content, order - all optional
    title: Optional[str] = None
    content: Optional[str] = None
    order: Optional[int] = None
    # course_id should generally not be updatable; move lesson by deleting/recreating


# Properties shared by models stored in DB
class LessonInDBBase(LessonBase):
    id: int
    course_id: int
    created_at: datetime
    updated_at: datetime

    # Pydantic V2 Config
    class Config:
        from_attributes = True
    # Pydantic V1 Config
    # class Config:
    #     orm_mode = True


# Properties to return to client
class Lesson(LessonInDBBase):
    pass  # Currently same as DB base, but could differ


# Properties stored in DB
class LessonInDB(LessonInDBBase):
    pass
