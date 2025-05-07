# app/models/course.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    # Optional: Link to the user who created the course
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship to User (optional)
    creator = relationship(
        "User")  # Add back_populates in User model if needed: courses_created = relationship("Course", back_populates="creator")

    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")

    # Relationship to Lessons (one-to-many)
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
