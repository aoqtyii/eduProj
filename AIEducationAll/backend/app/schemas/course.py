# app/schemas/course.py
from pydantic import BaseModel
from typing import Optional, List  # Use List for Python < 3.9
from datetime import datetime
from .lesson import Lesson  # Import Lesson schema


# Import Lesson schema later when defined
# from .lesson import Lesson

class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None


class CourseCreate(CourseBase):
    pass  # Currently no extra fields needed for creation besides base


class CourseUpdate(CourseBase):
    # Allow updating title and description
    title: Optional[str] = None  # Optional fields for update
    description: Optional[str] = None


# Properties shared by models stored in DB
class CourseInDBBase(CourseBase):
    id: int
    creator_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    # Pydantic V2 Config
    class Config:
        from_attributes = True
    # Pydantic V1 Config
    # class Config:
    #     orm_mode = True


# Properties to return to client (includes nested lessons later)
class Course(CourseInDBBase):
    lessons: List[Lesson] = []  # Add this when Lesson schema is defined
    pass


# Properties stored in DB
class CourseInDB(CourseInDBBase):
    pass


class CourseBasic(BaseModel):
    id: int
    title: str
    description: Optional[str] = None

    # 可以根据需要添加其他字段，如 thumbnail_url: Optional[str] = None

    # Pydantic V2 Config
    class Config:
        from_attributes = True
    # Pydantic V1 Config
    # class Config:
    #     orm_mode = True
