# app/api/endpoints/lessons.py
from fastapi import APIRouter, Depends, HTTPException, status, Response  # Import Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


# --- create_lesson ---
@router.post("/", response_model=schemas.Lesson, status_code=status.HTTP_201_CREATED)
async def create_lesson(
        *,
        db: AsyncSession = Depends(deps.get_db),
        lesson_in: schemas.LessonCreate,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Create a new lesson. Requires authentication and permission on the target course.
    """
    # 1. Check if the course exists and if user has permission
    course = await crud.course.get(db, id=lesson_in.course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {lesson_in.course_id} not found.",
        )

    # Authorization check: Must be course creator or superuser to add lessons
    if course.creator_id != current_user.id and not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to add lessons to this course")

    # 3. Create the lesson
    created_lesson = await crud.lesson.create(db=db, obj_in=lesson_in)
    return created_lesson


# --- read_lessons_by_course ---
@router.get("/by_course/{course_id}", response_model=List[schemas.Lesson])
async def read_lessons_by_course(
        *,
        db: AsyncSession = Depends(deps.get_db),
        course_id: int,
        skip: int = 0,
        limit: int = 100,
):
    # No permission change needed for listing (assuming public list within course)
    course = await crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found.",
        )
    lessons = await crud.lesson.get_multi_by_course(
        db, course_id=course_id, skip=skip, limit=limit
    )
    return lessons


# --- read_lesson ---
@router.get("/{lesson_id}", response_model=schemas.Lesson) #
async def read_lesson(
        *,
        db: AsyncSession = Depends(deps.get_db),
        lesson_id: int,
):
    lesson = await crud.lesson.get(db, id=lesson_id) #
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    # schemas.Lesson 包含了 content 字段
    return lesson

# --- update_lesson ---
@router.put("/{lesson_id}", response_model=schemas.Lesson)
async def update_lesson(
        *,
        db: AsyncSession = Depends(deps.get_db),
        lesson_id: int,
        lesson_in: schemas.LessonUpdate,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Update a lesson. Requires permission on the course the lesson belongs to.
    """
    lesson = await crud.lesson.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    # Fetch the course for permission check
    course = await crud.course.get(db, id=lesson.course_id)
    if not course:
        # Should not happen if lesson exists, but handle defensively
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated course not found")

    # Authorization check
    if course.creator_id != current_user.id and not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to update lessons in this course")

    # Proceed with update
    updated_lesson = await crud.lesson.update(db=db, db_obj=lesson, obj_in=lesson_in)
    return updated_lesson


# --- delete_lesson ---
# Corrected the route decorator typo here
@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
        *,
        db: AsyncSession = Depends(deps.get_db),
        lesson_id: int,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Delete a lesson. Requires permission on the course the lesson belongs to.
    """
    lesson = await crud.lesson.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    # Fetch the course for permission check
    course = await crud.course.get(db, id=lesson.course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated course not found")

    # Authorization check
    if course.creator_id != current_user.id and not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to delete lessons in this course")

    # Proceed with deletion
    await crud.lesson.remove(db=db, id=lesson_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)  # Return explicit 204 response