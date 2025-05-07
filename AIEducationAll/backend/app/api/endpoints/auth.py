# app/api/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import timedelta

from app import crud, schemas, models # Combined imports
from app.api import deps
from app.core.security import create_access_token, verify_password
from app.core.config import settings
# Import the specific crud modules needed
from app.crud import crud_password_reset_token, user as crud_user


router = APIRouter()


@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(deps.get_db)
):
    # 1. Find user
    user = await crud.user.get_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Check if active
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # 3. Create token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def register_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: schemas.UserRegister # Use the specific registration schema
):
    """
    Create new user.
    """
    existing_user = await crud.user.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    try:
        user = await crud.user.create(db=db, obj_in=user_in)
    except IntegrityError: # Catch potential race conditions
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists [race condition].",
        )
    except Exception as e:
         # Log the exception e
         print(f"Registration Error: {e}") # Basic logging
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration.",
        )

    return user


# Removed duplicate request_password_reset function definition
# Kept the more complete one below

# --- Forgot Password Endpoint ---
@router.post("/forgot-password")
async def request_password_reset(
    request_body: schemas.ForgotPasswordRequest,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Handles forgot password request. Finds user, creates reset token,
    and (ideally) sends email.
    """
    identifier = request_body.identifier
    user = await crud_user.get_by_identifier(db, identifier=identifier)

    reset_token_str = None # For testing purposes
    if user:
        db_token_obj = await crud_password_reset_token.create_password_reset_token(db, user_id=user.id)
        reset_token_str = db_token_obj.token

        # --- Email Sending Logic Placeholder ---
        print(f"Password reset requested for user: {user.email}. Token: {reset_token_str}")
        # In a real app, send an email here with the reset_token_str
        # --- End Placeholder ---

    response_message = "If an account with that email/username exists, a password reset link has been sent."
    response_data = {"message": response_message}
    # if reset_token_str: # REMOVE THIS IN PRODUCTION for security
    #     response_data["reset_token_for_testing"] = reset_token_str

    return response_data


# --- Reset Password Confirmation Endpoint ---
@router.post("/reset-password")
async def reset_password(
    *,
    db: AsyncSession = Depends(deps.get_db),
    reset_data: schemas.PasswordResetRequest = Body(...)
):
    """
    Reset password using a valid token.
    """
    token_str = reset_data.token
    new_password = reset_data.new_password

    db_token_obj = await crud_password_reset_token.get_reset_token_by_token(db, token=token_str)

    if not await crud_password_reset_token.is_token_valid(db_token_obj):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token.",
        )

    # We know db_token_obj is not None here
    user_to_reset = await crud_user.get(db, id=db_token_obj.user_id) # type: ignore
    if not user_to_reset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User associated with token not found.",
        )

    update_data = {"password": new_password}
    await crud_user.update(db=db, db_obj=user_to_reset, obj_in=update_data)

    await crud_password_reset_token.mark_token_as_used(db=db, db_token=db_token_obj) # type: ignore

    return {"message": "Password has been reset successfully."}