# app/models/progress.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)

    completed = Column(Boolean, default=False, nullable=False)
    score = Column(Float, nullable=True)  # Optional score (e.g., for quizzes within a lesson)
    last_accessed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)  # Timestamp when completed

    # Define relationships
    student = relationship("User", back_populates="progress")
    lesson = relationship("Lesson", back_populates="progress")

    # Ensure a user has only one progress record per lesson
    __table_args__ = (UniqueConstraint('user_id', 'lesson_id', name='uq_user_lesson_progress'),)

    def __repr__(self):
        return f"<Progress(user_id={self.user_id}, lesson_id={self.lesson_id}, completed={self.completed})>"
