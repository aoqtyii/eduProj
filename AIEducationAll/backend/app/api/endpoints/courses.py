# app/api/endpoints/courses.py
from fastapi import APIRouter, Depends, HTTPException, status, Response  # Import Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud, models, schemas
from app.api import deps
# 新增导入 selectinload
from sqlalchemy.orm import selectinload
# 新增导入 select
from sqlalchemy.future import select

router = APIRouter()


# --- create_course ---
@router.post("/", response_model=schemas.Course, status_code=status.HTTP_201_CREATED)
async def create_course(
        *,
        db: AsyncSession = Depends(deps.get_db),
        course_in: schemas.CourseCreate,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    # No permission change needed here usually, creator is assigned
    created_course = await crud.course.create_with_creator(
        db=db, obj_in=course_in, creator_id=current_user.id
    )
    return created_course


# --- read_courses ---
@router.get("/", response_model=List[schemas.Course])
async def read_courses(
        db: AsyncSession = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
):
    # No permission change needed for listing (assuming public list)
    # courses = await crud.course.get_multi(db, skip=skip, limit=limit)
    # --- 新增：直接在端点进行查询并预加载 lessons ---
    stmt = (
        select(models.Course)
        .options(selectinload(models.Course.lessons))  # <--- 预加载 lessons
        .order_by(models.Course.id)  # 或者其他排序方式
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    courses = result.scalars().unique().all()  # 使用 unique() 因为 selectinload 可能导致重复行

    return courses


# --- read_course ---
@router.get("/{course_id}", response_model=schemas.Course)
async def read_course(
        *,
        db: AsyncSession = Depends(deps.get_db),
        course_id: int,
):
    # No permission change needed for reading single (assuming public)
    # course = await crud.course.get(db, id=course_id)
    stmt = (
        select(models.Course)
        .options(selectinload(models.Course.lessons))  # <--- 预加载 lessons
        .filter(models.Course.id == course_id)
    )
    result = await db.execute(stmt)
    course = result.scalars().first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


# --- update_course ---
@router.put("/{course_id}", response_model=schemas.Course)
async def update_course(
        *,
        db: AsyncSession = Depends(deps.get_db),
        course_id: int,
        course_in: schemas.CourseUpdate,
        current_user: models.User = Depends(deps.get_current_active_user)  # Get current user
        # Course object fetched via dependency injection below
        # course: models.Course = Depends(deps.get_course_and_check_permissions) # Use dependency (Option 1)
):
    """
    Update a course. Requires user to be the course creator or a superuser.
    """
    # Option 2: Manual check within endpoint
    course = await crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    # Authorization check
    if course.creator_id != current_user.id and not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this course")

    # Proceed with update
    updated_course = await crud.course.update(db=db, db_obj=course, obj_in=course_in)
    return updated_course


# --- delete_course ---
@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
        *,
        db: AsyncSession = Depends(deps.get_db),
        course_id: int,
        current_user: models.User = Depends(deps.get_current_active_user)  # Get current user
        # course: models.Course = Depends(deps.get_course_and_check_permissions) # Use dependency (Option 1)
):
    """
    Delete a course. Requires user to be the course creator or a superuser.
    """
    # Option 2: Manual check within endpoint
    course = await crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    # Authorization check
    if course.creator_id != current_user.id and not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this course")

    # Proceed with deletion
    await crud.course.remove(db=db, id=course_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)  # Return explicit 204 response
