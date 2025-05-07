# app/crud/crud_progress.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone

from app.crud.base import CRUDBase
from app.models import Lesson
from app.models.progress import Progress
from app.schemas.progress import ProgressCreate, ProgressUpdate


class CRUDProgress(CRUDBase[Progress, ProgressCreate, ProgressUpdate]):

    async def get_by_user_and_lesson(
            self, db: AsyncSession, *, user_id: int, lesson_id: int
    ) -> Optional[Progress]:
        """Get progress for a specific user and lesson."""
        result = await db.execute(
            select(self.model)
            .filter(self.model.user_id == user_id, self.model.lesson_id == lesson_id)
        )
        return result.scalars().first()

    async def update_or_create_progress(
            self, db: AsyncSession, *, user_id: int, obj_in: ProgressUpdate, lesson_id: int
    ) -> Progress:
        db_obj = await self.get_by_user_and_lesson(db, user_id=user_id, lesson_id=lesson_id) #

        now = datetime.now(timezone.utc)
        update_data = obj_in.model_dump(exclude_unset=True) # 获取传入的数据

        if db_obj:  # 如果记录已存在
            # 总是更新最后访问时间
            db_obj.last_accessed_at = now #
            # 更新从输入模式接收到的字段 (completed, score)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            # 如果 completed 设置为 True 且之前未设置完成时间，则记录完成时间
            if update_data.get("completed") is True and db_obj.completed_at is None:
                db_obj.completed_at = now #
            elif update_data.get("completed") is False: # 如果标记为未完成，重置完成时间
                db_obj.completed_at = None #

        else:  # 如果记录不存在
            # 创建新的进度记录
            create_data = {
                "user_id": user_id,
                "lesson_id": lesson_id,
                "last_accessed_at": now, # 设置初始访问时间
                **update_data  # 应用来自更新模式的初始值
            }
            # 如果创建时 completed=True，设置完成时间
            if create_data.get("completed") is True:
                create_data["completed_at"] = now #

            db_obj = Progress(**create_data)

        db.add(db_obj)
        await db.flush()
        return db_obj

    async def get_progress_by_user_and_course(
            self, db: AsyncSession, *, user_id: int, course_id: int
    ) -> List[Progress]:
        """Get all progress records for a user within a specific course."""
        result = await db.execute(
            select(Progress)
            .join(Progress.lesson)  # Join with Lesson model
            .filter(Progress.user_id == user_id)
            .filter(Lesson.course_id == course_id)  # Filter by course_id via the joined Lesson
            # Optional: Eager load lesson details if needed
            # .options(selectinload(Progress.lesson))
        )
        return result.scalars().all()

    async def get_completed_lessons_count(
            self, db: AsyncSession, *, user_id: int, course_id: int
    ) -> int:
        """Counts completed lessons for a user in a course."""
        # Note: This can be optimized with a direct count query
        progress_records = await self.get_progress_by_user_and_course(
            db, user_id=user_id, course_id=course_id
        )
        return sum(1 for p in progress_records if p.completed)


# Instantiate the CRUD object
progress = CRUDProgress(Progress)
