# app/models/recommendation.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, SmallInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recommendation_type = Column(String(50), nullable=False, index=True) # 'practice_module', 'knowledge_point', etc.
    related_item_id = Column(Integer, nullable=True) # ID of module, knowledge_point, etc. Can be null if type is general
    related_item_name = Column(String(255), nullable=True) # Denormalized name
    reason = Column(Text, nullable=True)
    priority = Column(SmallInteger, default=0)
    status = Column(String(50), default='active', nullable=False, index=True) # 'active', 'dismissed', 'completed'
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User") # Define backref in User if needed