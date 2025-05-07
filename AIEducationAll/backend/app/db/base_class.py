# app/db/base_class.py (Create this if it doesn't exist)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func
from sqlalchemy import Column, DateTime, MetaData
from typing import Any

# Optional: Define naming convention for constraints for Alembic auto-generation
# https://alembic.sqlalchemy.org/en/latest/naming.html
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    metadata = metadata
    # You can add common fields or methods here if needed
    # id: Any # Often defined in subclasses
    pass

# Removed duplicated User model definition - it belongs in models/user.py