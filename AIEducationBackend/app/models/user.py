# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base  # Import Base from the central location


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), index=True, nullable=True)  # Allow null for full_name
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean(), default=True, nullable=False)
    is_superuser = Column(Boolean(), default=False, nullable=False)  # Optional admin flag

    # Auto-managed timestamps
    # server_default=func.now() sets the default value on the DB side
    # onupdate=func.now() updates the value on the DB side during UPDATE
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    # If you want to easily access courses created by this user:
    courses_created = relationship(
        "Course",
        back_populates="creator",
        cascade="all, delete-orphan",  # If a user is deleted, their courses are also deleted
        passive_deletes=True  # Needed for ON DELETE behavior in DB with some engines
    )

    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    progress = relationship("Progress", back_populates="student", cascade="all, delete-orphan")

    # Add other relationships here, e.g., enrollments, progress, etc.
    # password_reset_tokens = relationship("PasswordResetToken", backref="user", cascade="all, delete-orphan") # Can add backref if needed

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
