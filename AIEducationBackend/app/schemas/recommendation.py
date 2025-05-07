# app/schemas/recommendation.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RecommendationBase(BaseModel):
    recommendation_type: str
    related_item_id: Optional[int] = None
    related_item_name: Optional[str] = None
    reason: Optional[str] = None
    priority: Optional[int] = 0
    status: str = 'active'


class RecommendationCreate(RecommendationBase):
    user_id: int  # Needed when creating directly


class RecommendationUpdate(BaseModel):
    status: Optional[str] = None  # Allow updating status (e.g., dismissed)


class Recommendation(RecommendationBase):
    id: int
    user_id: int
    generated_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True
