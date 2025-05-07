# app/crud/crud_user.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Any, Dict, Optional, Union

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate  # Assume UserUpdate exists


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        result = await db.execute(select(self.model).filter(self.model.email == email))
        return result.scalars().first()

    async def get_by_identifier(self, db: AsyncSession, *, identifier: str) -> User | None:
        """ Helper to find user by email or potentially username if added later """
        # For now, assuming identifier is email
        return await self.get_by_email(db=db, email=identifier)

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=obj_in.is_active if hasattr(obj_in, 'is_active') else True,  # Use default if not provided
            # is_superuser=obj_in.is_superuser # Only set if needed
        )
        db.add(db_obj)
        await db.flush()
        return db_obj

    async def authenticate(
            self, db: AsyncSession, *, email: str, password: str
    ) -> User | None:
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def is_active(self, user: User) -> bool:
        return user.is_active

    async def is_superuser(self, user: User) -> bool:
        return user.is_superuser

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        # Convert Pydantic schema to dict if needed, excluding unset fields
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # Pydantic v2
            update_data = obj_in.model_dump(exclude_unset=True)
            # Pydantic v1
            # update_data = obj_in.dict(exclude_unset=True)

        # If password is being updated, hash it before saving
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"] # Remove plain password from dict
            update_data["hashed_password"] = hashed_password # Add hashed password

        # Call the base update method with the potentially modified update_data
        return await super().update(db=db, db_obj=db_obj, obj_in=update_data)


# Instantiate the CRUD object for users
user = CRUDUser(User)

# app/crud/__init__.py
# Make CRUD objects easily importable
from .crud_user import user
# Import other crud objects here
