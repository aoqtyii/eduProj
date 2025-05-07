# app/models/practice_module.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class PracticeModule(Base):
    __tablename__ = "practice_modules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    # Optional link back to a course
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="SET NULL"), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    course = relationship("Course")  # Relationship to Course model
    questions = relationship("PracticeQuestion", back_populates="module", cascade="all, delete-orphan")
    sessions = relationship("PracticeSession", back_populates="module", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PracticeModule(id={self.id}, title='{self.title}')>"
