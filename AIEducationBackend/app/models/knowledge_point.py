# app/models/knowledge_point.py
from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    subject_area = Column(String(100), index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship to the mapping table
    question_associations = relationship("QuestionKnowledgePoint", back_populates="knowledge_point")


class QuestionKnowledgePoint(Base):
    __tablename__ = "question_knowledge_points"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("practice_questions.id", ondelete="CASCADE"), nullable=False)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id", ondelete="CASCADE"), nullable=False)

    question = relationship("PracticeQuestion", back_populates="knowledge_point_associations")
    knowledge_point = relationship("KnowledgePoint", back_populates="question_associations")

    __table_args__ = (UniqueConstraint('question_id', 'knowledge_point_id', name='uq_question_knowledge_point'),)
