# app/api/endpoints/progress.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.post("/lesson/{lesson_id}", response_model=schemas.Progress)
async def update_lesson_progress(
        *,
        db: AsyncSession = Depends(deps.get_db),
        lesson_id: int,
        # progress_in 包含 completed?, score?
        # 当前端只为记录访问而调用时，可以传入空对象 {} 或只包含部分字段
        progress_in: schemas.ProgressUpdate,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Update or create progress for the current user on a specific lesson.
    This is typically called when a user finishes a lesson or interacts with it.
    """
    # 1. Check if the lesson exists
    lesson = await crud.lesson.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with id {lesson_id} not found.",
        )

    # 2. Check if the user is enrolled in the course this lesson belongs to (Important!)
    enrollment = await crud.enrollment.get_by_user_and_course(
        db, user_id=current_user.id, course_id=lesson.course_id
    )
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not enrolled in the course containing this lesson.",
        )

    # 3. Update or create the progress record
    updated_progress = await crud.progress.update_or_create_progress(
        db=db, user_id=current_user.id, lesson_id=lesson_id, obj_in=progress_in
    )

    return updated_progress

# You might add other endpoints, e.g., GET /progress/lesson/{lesson_id} to retrieve specific progress
