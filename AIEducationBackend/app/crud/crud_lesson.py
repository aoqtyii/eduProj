# app/crud/crud_lesson.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.crud.base import CRUDBase
from app.models.lesson import Lesson
from app.schemas.lesson import LessonCreate, LessonUpdate


class CRUDLesson(CRUDBase[Lesson, LessonCreate, LessonUpdate]):
    async def get_multi_by_course(
            self, db: AsyncSession, *, course_id: int, skip: int = 0, limit: int = 100
    ) -> List[Lesson]:
        result = await db.execute(
            select(self.model)
            .filter(self.model.course_id == course_id)
            # 关键：确保按顺序排序，这样 limit=1 就能拿到第一节课
            .order_by(self.model.order, self.model.id) #
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

# Instantiate the CRUD object
lesson = CRUDLesson(Lesson)
