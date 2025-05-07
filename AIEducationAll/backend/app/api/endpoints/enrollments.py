# app/api/endpoints/enrollments.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.Enrollment, status_code=status.HTTP_201_CREATED)
async def enroll_in_course(
    *,
    db: AsyncSession = Depends(deps.get_db),
    enrollment_in: schemas.EnrollmentCreate, # Expects {"course_id": N}
    current_user: models.User = Depends(deps.get_current_active_user) # Require login
):
    """
    Enroll the current user in a specified course.
    """
    course_id = enrollment_in.course_id
    user_id = current_user.id

    # 1. Check if the course exists
    course = await crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found.",
        )

    # 2. Attempt to create the enrollment
    try:
        # crud.enrollment.create_enrollment handles check for existing enrollment
        created_enrollment = await crud.enrollment.create_enrollment(
            db=db, user_id=user_id, course_id=course_id
        )
    except IntegrityError: # Catch potential race condition on unique constraint
         raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already enrolled in this course [race condition].",
         )
    except Exception as e:
        # Log the exception e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during enrollment.",
        )

    # You might want to load the course relationship before returning
    # await db.refresh(created_enrollment, attribute_names=['course']) # If needed by schema
    return created_enrollment


@router.get("/me", response_model=List[schemas.EnrollmentPublic])
async def read_my_enrollments(
    *,
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    获取当前用户的课程报名列表，包含课程基本信息。
    """
    # crud.enrollment.get_multi_by_user 现在会预加载课程信息
    enrollments = await crud.enrollment.get_multi_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    # Pydantic 会自动处理从 Enrollment 模型到 EnrollmentPublic Schema 的转换
    # 包括嵌套的 course 对象 (因为它现在在 EnrollmentPublic 中定义了)
    return enrollments


@router.delete("/course/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unenroll_from_course(
    *,
    db: AsyncSession = Depends(deps.get_db),
    course_id: int,
    current_user: models.User = Depends(deps.get_current_active_user) # Require login
):
    """
    Unenroll the current user from a specified course.
    """
    deleted_enrollment = await crud.enrollment.remove_enrollment(
        db=db, user_id=current_user.id, course_id=course_id
    )
    if not deleted_enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found for this user and course.",
        )
    return None # Or return Response(status_code=status.HTTP_204_NO_CONTENT)

# Potential endpoint for admins/teachers:
# @router.get("/by_course/{course_id}", response_model=List[schemas.Enrollment])
# async def read_course_enrollments(...): ...