# app/models/practice_session.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    module_id = Column(Integer, ForeignKey("practice_modules.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    score = Column(Float, nullable=True)
    status = Column(String(50), default='in_progress', nullable=False, index=True)  # 'in_progress', 'completed'

    # Relationships
    user = relationship("User")  # Add backref in User if needed
    module = relationship("PracticeModule", back_populates="sessions")
    attempts = relationship("PracticeAttempt", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PracticeSession(id={self.id}, user_id={self.user_id}, module_id={self.module_id}, status='{self.status}')>"
