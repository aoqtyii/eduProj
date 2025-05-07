# app/models/enrollment.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    enrollment_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Define relationships
    student = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

    # Ensure a user can only enroll in a course once
    __table_args__ = (UniqueConstraint('user_id', 'course_id', name='uq_user_course_enrollment'),)

    def __repr__(self):
        return f"<Enrollment(user_id={self.user_id}, course_id={self.course_id})>"
