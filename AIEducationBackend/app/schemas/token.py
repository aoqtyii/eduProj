# app/schemas/token.py
from pydantic import BaseModel
from typing import Optional # Use Optional for Python < 3.10

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None # Optional[str] in < 3.10, str | None = None in >= 3.10 # Usually user id or username

# Removed duplicated User schemas - they belong in schemas/user.py