# app/api/deps.py
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt # Corrected import, JWTError might be needed too from jose

from app.core import security
from app.core.config import settings
from app.db.session import get_async_db_session
from app.models.user import User
from app.schemas.token import TokenPayload
from app import crud, models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_async_db_session():
        yield session

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.decode_token(token)
        if payload is None:
            raise credentials_exception
        token_data = TokenPayload(**payload)
        if token_data.sub is None:
            raise credentials_exception
    except jwt.JWTError: # Catch potential decoding errors
        raise credentials_exception

    user_id = int(token_data.sub)
    user = await crud.user.get(db, id=user_id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    # crud.user.is_active is synchronous, no await needed based on previous definition
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Dependency for superuser access
async def get_current_active_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    # crud.user.is_superuser is synchronous
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, # Use 403 Forbidden for authorization errors
            detail="The user doesn't have enough privileges"
        )
    return current_user

# Optional: Dependency to get a course and check ownership/admin status
async def get_course_and_check_permissions(
    *,
    db: AsyncSession = Depends(get_db),
    course_id: int,
    current_user: models.User = Depends(get_current_active_user)
) -> models.Course:
    course = await crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if course.creator_id != current_user.id and not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this course")
    return course