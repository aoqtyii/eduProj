# app/crud/crud_knowledge_point.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.knowledge_point import KnowledgePoint, QuestionKnowledgePoint
from app.schemas.knowledge_point import KnowledgePointCreate  # Assuming no update schema for now


class CRUDKnowledgePoint(CRUDBase[KnowledgePoint, KnowledgePointCreate, KnowledgePointCreate]):
    # Add specific methods if needed, e.g., find by name
    async def get_by_name(self, db: AsyncSession, *, name: str) -> KnowledgePoint | None:
        result = await db.execute(select(self.model).filter(self.model.name == name))
        return result.scalars().first()

    # You might add methods to manage the question_knowledge_points mapping


knowledge_point = CRUDKnowledgePoint(KnowledgePoint)

# Add CRUD for the mapping table if complex operations are needed,
# otherwise direct session operations might suffice in services.
