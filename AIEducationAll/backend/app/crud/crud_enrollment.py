# app/crud/crud_enrollment.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from sqlalchemy.orm import selectinload  # For eager loading related objects

from app.crud.base import CRUDBase
from app.models.enrollment import Enrollment
from app.schemas.enrollment import EnrollmentCreate  # Use specific schema if needed, Base likely sufficient here


# Note: Enrollment doesn't typically need Update schema/logic
class CRUDEnrollment(CRUDBase[Enrollment, EnrollmentCreate, EnrollmentCreate]):  # Using Create schema for Update slot

    async def create_enrollment(
            self, db: AsyncSession, *, user_id: int, course_id: int
    ) -> Enrollment:
        """Creates an enrollment record."""
        # Check if already enrolled (handled by UniqueConstraint, but good practice)
        existing = await self.get_by_user_and_course(db, user_id=user_id, course_id=course_id)
        if existing:
            # Decide whether to return existing or raise error
            # Returning existing might be acceptable
            return existing
            # Or raise error:
            # from fastapi import HTTPException, status
            # raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already enrolled in this course")

        db_obj = Enrollment(user_id=user_id, course_id=course_id)
        db.add(db_obj)
        await db.flush()
        return db_obj

    async def get_by_user_and_course(
            self, db: AsyncSession, *, user_id: int, course_id: int
    ) -> Optional[Enrollment]:
        """Check if a specific enrollment exists."""
        result = await db.execute(
            select(self.model)
            .filter(self.model.user_id == user_id, self.model.course_id == course_id)
        )
        return result.scalars().first()

    async def get_multi_by_user(
            self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Enrollment]:
        """获取指定用户的所有报名记录，并预加载课程信息。"""
        result = await db.execute(
            select(self.model)
            .filter(self.model.user_id == user_id)
            .order_by(self.model.enrollment_date.desc())
            # --- 修改点：添加 options(selectinload(...)) ---
            .options(selectinload(self.model.course))  # 预加载关联的 Course 对象
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def remove_enrollment(
            self, db: AsyncSession, *, user_id: int, course_id: int
    ) -> Optional[Enrollment]:
        """Removes a specific enrollment."""
        obj = await self.get_by_user_and_course(db, user_id=user_id, course_id=course_id)
        if obj:
            await db.delete(obj)
            await db.flush()
        return obj


# Instantiate the CRUD object
enrollment = CRUDEnrollment(Enrollment)
