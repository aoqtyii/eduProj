# app/crud/crud_course.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func # Import func for count


from app.crud.base import CRUDBase
from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate


class CRUDCourse(CRUDBase[Course, CourseCreate, CourseUpdate]):
    # Add course-specific methods here if needed, e.g., find by title
    async def get_by_title(self, db: AsyncSession, *, title: str) -> Course | None:
        result = await db.execute(select(self.model).filter(self.model.title == title))
        return result.scalars().first()

    # Override create to potentially add creator_id
    async def create_with_creator(self, db: AsyncSession, *, obj_in: CourseCreate, creator_id: int) -> Course:
        db_obj = Course(
            **obj_in.model_dump(),  # Pydantic v2
            # **obj_in.dict(), # Pydantic v1
            creator_id=creator_id
        )
        db.add(db_obj)
        await db.flush()
        return db_obj

    async def get_lesson_count_by_course(self, db: AsyncSession, *, course_id: int) -> int:
        """Counts the total number of lessons in a specific course."""
        result = await db.execute(
            select(func.count(self.model.id))  # Use func.count
            .filter(self.model.course_id == course_id)
        )
        return result.scalar_one_or_none() or 0  # Return count or 0 if None

# Instantiate the CRUD object
course = CRUDCourse(Course)
