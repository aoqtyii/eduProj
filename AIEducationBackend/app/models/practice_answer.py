# app/models/practice_answer.py
from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, SmallInteger
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class PracticeAnswer(Base):
    __tablename__ = "practice_answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("practice_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    answer_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    display_order = Column(SmallInteger, default=0)  # For ordering multiple choice options

    # Relationships
    question = relationship("PracticeQuestion", back_populates="answers")
    attempts = relationship("PracticeAttempt", back_populates="selected_answer")  # Link attempts that chose this answer

    def __repr__(self):
        return f"<PracticeAnswer(id={self.id}, question_id={self.question_id}, correct={self.is_correct})>"
