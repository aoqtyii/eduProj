# app/schemas/knowledge_point.py
from pydantic import BaseModel
from typing import Optional


class KnowledgePointBase(BaseModel):
    name: str
    description: Optional[str] = None
    subject_area: Optional[str] = None


class KnowledgePointCreate(KnowledgePointBase):
    pass


class KnowledgePoint(KnowledgePointBase):
    id: int

    # created_at: datetime # Optional

    class Config:
        from_attributes = True
