# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field  # Import Field if needed for validation
from typing import Optional  # Use Optional for Python < 3.10


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None  # Optional in Python < 3.10, str | None = None in >= 3.10
    is_active: Optional[bool] = True  # Optional in Python < 3.10, bool | None = True in >= 3.10


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)  # Add password validation if desired


# Schema for registration requests from the frontend
# Can be the same as UserCreate or have slight variations if needed
class UserRegister(UserCreate):
    pass  # Inherits fields and validation from UserCreate


# Schema for updating user information (e.g., profile update)
# All fields are optional for updates
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None  # Optional in Python < 3.10, EmailStr | None = None in >= 3.10
    full_name: Optional[str] = None  # Optional in Python < 3.10, str | None = None in >= 3.10
    password: Optional[str] = None  # Optional in Python < 3.10, str | None = None in >= 3.10, Field(None, min_length=8)
    is_active: Optional[bool] = None  # Optional in Python < 3.10, bool | None = None in >= 3.10
    # is_superuser: Optional[bool] = None # Allow updating superuser status? Be careful.


# Schema for representing a user returned by the API (excluding password)
class User(UserBase):
    id: int

    # is_superuser: bool # Include if needed

    # Pydantic V2 config
    class Config:
        from_attributes = True
    # Pydantic V1 config
    # class Config:
    #     orm_mode = True


# Schema including hashed_password (used internally, not returned by API)
class UserInDB(User):
    hashed_password: str
