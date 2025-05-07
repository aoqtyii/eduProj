# app/crud/crud_recommendation.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.crud.base import CRUDBase
from app.models.recommendation import Recommendation
from app.schemas.recommendation import RecommendationCreate, RecommendationUpdate


class CRUDRecommendation(CRUDBase[Recommendation, RecommendationCreate, RecommendationUpdate]):

    async def get_multi_by_user(
            self, db: AsyncSession, *, user_id: int, status: str = 'active', skip: int = 0, limit: int = 10
    ) -> List[Recommendation]:
        """ Gets active recommendations for a user """
        stmt = (
            select(self.model)
            .filter(self.model.user_id == user_id, self.model.status == status)
            .order_by(self.model.priority.desc(), self.model.generated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create_recommendation(self, db: AsyncSession, *, obj_in: RecommendationCreate) -> Recommendation:
        # Could add logic here to prevent duplicate active recommendations if needed
        return await super().create(db=db, obj_in=obj_in)

    async def update_status(self, db: AsyncSession, *, db_obj: Recommendation, status: str) -> Recommendation:
        """ Updates the status of a recommendation """
        update_data = RecommendationUpdate(status=status)
        return await super().update(db=db, db_obj=db_obj, obj_in=update_data)


recommendation = CRUDRecommendation(Recommendation)
