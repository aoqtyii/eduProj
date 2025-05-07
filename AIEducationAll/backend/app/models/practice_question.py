# app/models/practice_question.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, SmallInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
from .practice_answer import PracticeAnswer


class PracticeQuestion(Base):
    __tablename__ = "practice_questions"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("practice_modules.id", ondelete="CASCADE"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False, index=True)  # e.g., 'multiple_choice', 'coding'
    difficulty = Column(SmallInteger, default=1)
    hints = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)  # Explanation shown after submission

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    module = relationship("PracticeModule", back_populates="questions")
    answers = relationship(
        "PracticeAnswer",
        back_populates="question",
        cascade="all, delete-orphan",
        # 添加这行来指定答案的默认排序 (按显示顺序，然后按ID)
        order_by="PracticeAnswer.display_order, PracticeAnswer.id"  #
    )
    attempts = relationship("PracticeAttempt", back_populates="question", cascade="all, delete-orphan")
    knowledge_point_associations = relationship("QuestionKnowledgePoint", back_populates="question", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PracticeQuestion(id={self.id}, type='{self.question_type}', module_id={self.module_id})>"
