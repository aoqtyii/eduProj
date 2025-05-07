# 文件: AIEducationAll/backend/app/api/endpoints/dashboard.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload  # 导入 eager loading 相关函数
from typing import List, Optional

from app import crud, models, schemas  # 确保 schemas 已导入
from app.api import deps
from datetime import datetime, timedelta  # 导入 datetime

# 导入或定义来自步骤 1 的 Schema
# 选项 1: 如果在 schemas/dashboard.py 中创建了，则导入
# from app.schemas.dashboard import StudentDashboardData, DashboardCourseProgress, DashboardRecentActivity
# 选项 2: 如果不使用单独的文件，则在此直接定义 Pydantic 模型 (如步骤 1 所示)
from pydantic import BaseModel  # 如果内联定义 Schema，添加此导入


# 如果没有创建 schemas/dashboard.py，在此直接定义 Schema
class DashboardCourseProgress(BaseModel):
    course_id: int
    course_title: str
    total_lessons: int = 0
    completed_lessons: int = 0
    progress_percentage: int = 0


class DashboardRecentActivity(BaseModel):
    activity_type: str
    item_id: int
    item_title: str
    timestamp: datetime
    course_title: Optional[str] = None


class StudentDashboardData(BaseModel):
    enrolled_courses_progress: List[DashboardCourseProgress] = []
    recent_activity: List[DashboardRecentActivity] = []
    # 稍后添加其他字段


router = APIRouter()


@router.get("/student", response_model=StudentDashboardData)
async def read_student_dashboard(
        db: AsyncSession = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    获取学生 Dashboard 的增强摘要数据，
    包括每个已报名课程的进度和最近活动。
    """
    user_id = current_user.id
    dashboard_data = StudentDashboardData()

    # --- 1. 获取已报名课程并计算进度 ---
    # 获取用户的报名记录
    enrollments = await crud.enrollment.get_multi_by_user(
        db,
        user_id=user_id,
        limit=50  # 如果需要，限制直接在 Dashboard 上显示的课程数量
    )

    if not enrollments:
        return dashboard_data  # 如果没有报名，返回空的 Dashboard 数据

    enrolled_course_ids = [e.course_id for e in enrollments]

    # 高效地获取所有已报名课程的所有课时
    stmt_lessons = (
        select(models.Lesson)
        # 预加载课程信息以获取标题
        .options(joinedload(models.Lesson.course))
        .filter(models.Lesson.course_id.in_(enrolled_course_ids))
        .order_by(models.Lesson.course_id, models.Lesson.order)  # 按课程和顺序排序
    )
    result_lessons = await db.execute(stmt_lessons)
    all_lessons = result_lessons.scalars().all()

    # 高效地获取用户在这些课时上的所有进度记录
    lesson_ids = [l.id for l in all_lessons]
    stmt_progress = (
        select(models.Progress)
        .filter(models.Progress.user_id == user_id, models.Progress.lesson_id.in_(lesson_ids))
    )
    result_progress = await db.execute(stmt_progress)
    all_progress = result_progress.scalars().all()
    # 将 lesson_id 映射到进度记录，方便查找
    progress_map = {p.lesson_id: p for p in all_progress}

    # 按 course_id 分组课时
    lessons_by_course = {}
    for lesson in all_lessons:
        if lesson.course_id not in lessons_by_course:
            # 初始化课程数据，存储课时列表和课程标题
            lessons_by_course[lesson.course_id] = {"lessons": [], "course_title": lesson.course.title}
        lessons_by_course[lesson.course_id]["lessons"].append(lesson)

    # 计算每门课程的进度
    for course_id, course_data in lessons_by_course.items():
        total_lessons = len(course_data["lessons"])  # 该课程的总课时数
        completed_lessons = 0  # 已完成课时数
        # 遍历该课程的所有课时
        for lesson in course_data["lessons"]:
            # 从 progress_map 中查找该课时的进度记录
            progress_record = progress_map.get(lesson.id)
            # 如果找到记录且状态为已完成，则计数加一
            if progress_record and progress_record.completed:
                completed_lessons += 1

        # 计算完成百分比
        progress_percentage = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0

        # 将课程进度信息添加到 Dashboard 数据中
        dashboard_data.enrolled_courses_progress.append(
            DashboardCourseProgress(
                course_id=course_id,
                course_title=course_data["course_title"],
                total_lessons=total_lessons,
                completed_lessons=completed_lessons,
                progress_percentage=progress_percentage,
            )
        )

    # --- 2. 获取最近活动 (示例: 最近访问的 5 个课时) ---
    # 获取最近的进度记录，按最后访问时间降序排序
    recent_progress_stmt = (
        select(models.Progress)
        .options(
            # 预加载课时及其所属课程的信息以获取标题
            selectinload(models.Progress.lesson).joinedload(models.Lesson.course)
        )
        .filter(models.Progress.user_id == user_id)
        .order_by(models.Progress.last_accessed_at.desc())
        .limit(5)  # 限制为最近 5 条活动
    )
    result_recent_progress = await db.execute(recent_progress_stmt)
    recent_progress_records = result_recent_progress.scalars().all()

    # 格式化最近活动数据
    for p in recent_progress_records:
        # 确保课时和课程数据已加载
        lesson_title = p.lesson.title if p.lesson else "未知课时"
        course_title = p.lesson.course.title if p.lesson and p.lesson.course else "未知课程"

        dashboard_data.recent_activity.append(
            DashboardRecentActivity(
                activity_type="lesson_accessed",  # 或根据你的逻辑设置更具体的类型
                item_id=p.lesson_id,
                item_title=lesson_title,
                timestamp=p.last_accessed_at,
                course_title=course_title
            )
        )

    # 如果需要，可以按课程标题或其他标准对课程进度列表进行排序
    dashboard_data.enrolled_courses_progress.sort(key=lambda x: x.course_title)

    return dashboard_data
