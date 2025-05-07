# 文件: AIEducationAll/backend/app/models/mistake_notebook_entry.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
from datetime import datetime

class MistakeNotebookEntry(Base):
    __tablename__ = "mistake_notebook_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("practice_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    # original_attempt_id = Column(Integer, ForeignKey("practice_attempts.id", ondelete="SET NULL"), nullable=True)

    added_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(String(50), default='new', nullable=False, index=True)  # 'new', 'reviewed', 'mastered'
    notes = Column(Text, nullable=True)
    last_reviewed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User") # Add backref in User model if needed
    question = relationship("PracticeQuestion") # Add backref in PracticeQuestion model if needed
    # original_attempt = relationship("PracticeAttempt") # If using original_attempt_id

    # Unique constraint defined in SQL via __table_args__ in model or directly in SQL
    __table_args__ = (UniqueConstraint('user_id', 'question_id', name='uq_user_question_mistake'),)

    def __repr__(self):
        return f"<MistakeNotebookEntry(id={self.id}, user_id={self.user_id}, question_id={self.question_id}, status='{self.status}')>"