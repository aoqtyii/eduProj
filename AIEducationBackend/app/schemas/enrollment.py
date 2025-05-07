# 文件: AIEducationAll/backend/app/schemas/enrollment.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# 导入相关 Schema
# from .user import User # 通常不在此暴露完整 User
from .course import CourseBasic  # <--- 使用简化的 CourseBasic Schema


class EnrollmentBase(BaseModel):
    course_id: int
    # user_id 在创建时从上下文中获取


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentInDBBase(EnrollmentBase):
    id: int
    user_id: int
    enrollment_date: datetime

    class Config:
        from_attributes = True


# 返回给客户端的完整报名信息 (可能包含嵌套对象)
class Enrollment(EnrollmentInDBBase):
    # 可以选择性包含嵌套信息，但要注意数据大小和循环引用
    # student: Optional[User] = None
    course: Optional[CourseBasic] = None  # <--- 现在嵌套 CourseBasic


# 用于列表的公开报名信息 (例如 /enrollments/me)
class EnrollmentPublic(BaseModel):
    id: int
    user_id: int  # 对于 'me' 路由，这有点多余，但保留以保持一致性
    course_id: int
    enrollment_date: datetime
    course: Optional[CourseBasic] = None  # <--- 包含简化的课程信息

    class Config:
        from_attributes = True

# --- 更新 __init__.py ---
# 确保在 AIEducationAll/backend/app/schemas/__init__.py 中导出的 EnrollmentPublic 是最新的
# from .enrollment import Enrollment, EnrollmentCreate, EnrollmentPublic # 确保导出的正确
