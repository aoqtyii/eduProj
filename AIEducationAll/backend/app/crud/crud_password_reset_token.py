# app/crud/crud_password_reset_token.py
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.password_reset_token import PasswordResetToken

# Configuration for token expiry (e.g., 1 hour)
PASSWORD_RESET_TOKEN_EXPIRE_HOURS = 1


def generate_reset_token() -> str:
    """Generates a secure random token."""
    return secrets.token_urlsafe(32)


async def create_password_reset_token(db: AsyncSession, *, user_id: int) -> PasswordResetToken:
    """Creates and stores a new password reset token for a user."""
    token_str = generate_reset_token()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
    db_token = PasswordResetToken(
        user_id=user_id,
        token=token_str,
        expires_at=expires_at,
        used=False
    )
    db.add(db_token)
    await db.flush()  # Persist to DB within the transaction
    return db_token


async def get_reset_token_by_token(db: AsyncSession, *, token: str) -> PasswordResetToken | None:
    """Retrieves a token object by its token string."""
    result = await db.execute(
        select(PasswordResetToken).filter(PasswordResetToken.token == token)
    )
    return result.scalars().first()


async def mark_token_as_used(db: AsyncSession, *, db_token: PasswordResetToken) -> PasswordResetToken:
    """Marks a specific token object as used."""
    db_token.used = True
    db_token.expires_at = datetime.now(timezone.utc)  # Optionally expire immediately once used
    db.add(db_token)
    await db.flush()
    return db_token


async def is_token_valid(token_obj: PasswordResetToken | None) -> bool:
    """Checks if a token object exists, is not used, and has not expired."""
    return (
            token_obj is not None and
            not token_obj.used and
            token_obj.expires_at > datetime.now(timezone.utc)
    )

# Optional: Add functions to remove expired/used tokens periodically

# You might want an instantiated object like with users, or use functions directly
# password_reset_token = CRUDPasswordResetToken(PasswordResetToken)
