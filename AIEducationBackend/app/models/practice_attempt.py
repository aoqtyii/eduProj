# app/models/practice_attempt.py
from sqlalchemy import Column, Integer, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class PracticeAttempt(Base):
    __tablename__ = "practice_attempts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("practice_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("practice_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_answer_text = Column(Text, nullable=True)  # For free text or coding answers
    selected_answer_id = Column(Integer, ForeignKey("practice_answers.id", ondelete="SET NULL"), nullable=True,
                                index=True)  # For MCQs
    is_correct = Column(Boolean, nullable=True)  # Nullable until graded
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    feedback = Column(Text, nullable=True)  # Specific feedback if grading provides it

    # Relationships
    session = relationship("PracticeSession", back_populates="attempts")
    question = relationship("PracticeQuestion", back_populates="attempts")
    selected_answer = relationship("PracticeAnswer", back_populates="attempts")  # Link back to the chosen answer option

    def __repr__(self):
        return f"<PracticeAttempt(id={self.id}, session_id={self.session_id}, question_id={self.question_id}, correct={self.is_correct})>"
