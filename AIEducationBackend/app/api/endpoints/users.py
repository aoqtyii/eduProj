# app/api/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/me", response_model=schemas.User)
async def read_users_me(
        # Dependency automatically handles token validation and fetching the user
        current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get current logged-in user's profile information.
    """
    # The dependency already provides the user object.
    # The response_model=schemas.User ensures only safe fields are returned.
    return current_user


@router.put("/me", response_model=schemas.User)
async def update_user_me(
        *,
        db: AsyncSession = Depends(deps.get_db),
        user_in: schemas.UserUpdate,  # The schema with optional fields for update
        current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Update own user profile information.
    """
    # Check if email is being updated to an existing one
    if user_in.email and user_in.email != current_user.email:
        existing_user = await crud.user.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists.",
            )

    # Use the CRUD update function. It handles password hashing if provided.
    try:
        updated_user = await crud.user.update(db=db, db_obj=current_user, obj_in=user_in)
    except IntegrityError:  # Catch potential race condition on email update
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists [race condition].",
        )
    except Exception as e:
        # Log the exception e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the profile.",
        )

    return updated_user

# You could add other user-related endpoints here later, e.g.,
# - Get specific user by ID (admin only)
# - List users (admin only)
# - Update user (admin only)
# - Delete user (admin only)
