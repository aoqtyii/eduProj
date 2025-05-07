# app/schemas/password.py
from pydantic import BaseModel, Field


class PasswordResetRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class ForgotPasswordRequest(BaseModel):
    identifier: str  # Can be email or username
