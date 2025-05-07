# AIEducationAll/backend/app/services/ai_analysis_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, case, cast, Float, Integer, desc # 导入 desc
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone

from app import models, schemas, crud # 导入 crud
from app.schemas import ai_analysis as ai_schemas # 使用别名
from app.schemas import recommendation as rec_schemas
from app.schemas import practice as practice_schemas
from app.services import recommendation_service


async def get_student_ai_dashboard_data(db: AsyncSession, user_id: int) -> ai_schemas.StudentAIDashboardData: # 返回更新后的 Schema
    """
    获取学生的 AI 分析统计数据 Dashboard。
    """
    # 初始化返回结构
    dashboard_data = ai_schemas.StudentAIDashboardData(
        core_metrics=ai_schemas.CoreMetrics(),
        ongoing_courses_progress=[],
        recent_activity=[],
        practice_performance_summary=ai_schemas.PracticePerformanceSummary(),
        practice_performance_by_module=[],
        mistake_analysis_summary=ai_schemas.MistakeAnalysisSummary(),
        active_recommendations=[]
    )

    # --- 1. 获取基础数据：报名、所有相关课时、所有相关进度 ---
    enrollments = await crud.enrollment.get_multi_by_user(db, user_id=user_id, limit=1000) # 获取所有报名
    enrolled_course_ids = [e.course_id for e in enrollments]
    if not enrolled_course_ids:
        return dashboard_data # 没有报名的用户直接返回空 Dashboard

    # 所有已报名课程的课时 (包含课程信息)
    stmt_lessons = (
        select(models.Lesson)
        .options(joinedload(models.Lesson.course))
        .filter(models.Lesson.course_id.in_(enrolled_course_ids))
    )
    result_lessons = await db.execute(stmt_lessons)
    all_lessons = result_lessons.scalars().unique().all()
    lesson_map = {l.id: l for l in all_lessons} # lesson_id -> lesson 对象
    lessons_by_course: Dict[int, Dict] = {}
    for lesson in all_lessons:
        if lesson.course_id not in lessons_by_course:
            lessons_by_course[lesson.course_id] = {"lessons": [], "course_title": lesson.course.title}
        lessons_by_course[lesson.course_id]["lessons"].append(lesson)

    # 用户在这些课时上的所有进度
    lesson_ids = list(lesson_map.keys())
    stmt_progress = (
        select(models.Progress)
        .filter(models.Progress.user_id == user_id, models.Progress.lesson_id.in_(lesson_ids))
    )
    result_progress = await db.execute(stmt_progress)
    all_progress = result_progress.scalars().all()
    progress_map = {p.lesson_id: p for p in all_progress} # lesson_id -> progress 对象

    # --- 2. 计算核心指标 和 进行中的课程进度 ---
    total_progress_sum = 0
    total_courses_count = len(lessons_by_course)
    completed_courses_count = 0

    for course_id, course_data in lessons_by_course.items():
        total_lessons = len(course_data["lessons"])
        completed_lessons = 0
        last_access_time: Optional[datetime] = None
        for lesson in course_data["lessons"]:
            progress_record = progress_map.get(lesson.id)
            if progress_record:
                 if progress_record.completed:
                     completed_lessons += 1
                 if last_access_time is None or progress_record.last_accessed_at > last_access_time:
                     last_access_time = progress_record.last_accessed_at

        progress_percentage = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
        total_progress_sum += progress_percentage

        if progress_percentage < 100: # 只显示未完成的课程
            dashboard_data.ongoing_courses_progress.append(
                ai_schemas.DashboardCourseProgress(
                    course_id=course_id,
                    course_title=course_data["course_title"],
                    total_lessons=total_lessons,
                    completed_lessons=completed_lessons,
                    progress_percentage=progress_percentage,
                    last_accessed_at=last_access_time
                )
            )
        else:
             completed_courses_count += 1

    dashboard_data.core_metrics.average_progress = int(total_progress_sum / total_courses_count) if total_courses_count > 0 else 0
    # 按进度升序排序，优先显示进度低的
    dashboard_data.ongoing_courses_progress.sort(key=lambda x: x.progress_percentage)


    # --- 3. 获取近期活动 (合并多种类型并排序) ---
    recent_activities_list = []
    # a) 最近访问的课时
    recent_progress_records = sorted(
        [p for p in all_progress if p.last_accessed_at], # 过滤掉没有访问时间的记录
        key=lambda p: p.last_accessed_at,
        reverse=True
    )[:3] # 获取最近3条访问记录
    for p in recent_progress_records:
        lesson = lesson_map.get(p.lesson_id)
        if lesson and lesson.course:
            recent_activities_list.append(ai_schemas.DashboardRecentActivity(
                activity_type='lesson_accessed',
                item_id=p.lesson_id,
                item_title=lesson.title,
                timestamp=p.last_accessed_at,
                details={"course_title": lesson.course.title}
            ))

    # b) 最近完成的练习
    recent_sessions_stmt = (
        select(models.PracticeSession)
        .options(joinedload(models.PracticeSession.module))
        .filter(models.PracticeSession.user_id == user_id, models.PracticeSession.status == 'completed')
        .order_by(desc(models.PracticeSession.completed_at)) # 使用 desc
        .limit(3)
    )
    recent_sessions_result = await db.execute(recent_sessions_stmt)
    recent_sessions = recent_sessions_result.scalars().unique().all()
    for sess in recent_sessions:
        if sess.module and sess.completed_at:
            recent_activities_list.append(ai_schemas.DashboardRecentActivity(
                activity_type='practice_completed',
                item_id=sess.id, # 使用 session_id
                item_title=sess.module.title,
                timestamp=sess.completed_at,
                details={"score": sess.score}
            ))

    # c) 最近添加的错题
    recent_mistakes_stmt = (
        select(models.MistakeNotebookEntry)
        .options(joinedload(models.MistakeNotebookEntry.question).joinedload(models.PracticeQuestion.module))
        .filter(models.MistakeNotebookEntry.user_id == user_id)
        .order_by(desc(models.MistakeNotebookEntry.added_at)) # 使用 desc
        .limit(2)
    )
    recent_mistakes_result = await db.execute(recent_mistakes_stmt)
    recent_mistakes = recent_mistakes_result.scalars().unique().all()
    for entry in recent_mistakes:
        if entry.question:
            recent_activities_list.append(ai_schemas.DashboardRecentActivity(
                activity_type='mistake_added',
                item_id=entry.question_id,
                item_title=entry.question.question_text[:50] + ('...' if len(entry.question.question_text) > 50 else ''),
                timestamp=entry.added_at,
                details={"module_title": entry.question.module.title if entry.question.module else None}
            ))

    # 排序所有活动并取最新 5 条
    recent_activities_list.sort(key=lambda x: x.timestamp, reverse=True)
    dashboard_data.recent_activity = recent_activities_list[:5]


    # --- 4. 练习表现分析 ---
    # a. 整体表现 和 最近分数趋势
    stmt_overall = (
        select(
            func.count(models.PracticeSession.id).label("total_sessions"),
            func.avg(models.PracticeSession.score).label("average_score"), # 计算平均分
            func.sum(case((models.PracticeAttempt.is_correct == True, 1), else_=0)).label("correct_answers"),
            func.count(models.PracticeAttempt.id).label("total_attempts")
        )
        .select_from(models.PracticeSession)
        .outerjoin(models.PracticeAttempt, models.PracticeSession.id == models.PracticeAttempt.session_id)
        .filter(models.PracticeSession.user_id == user_id, models.PracticeSession.status == 'completed')
    )
    overall_result = await db.execute(stmt_overall)
    overall_stats = overall_result.first()

    if overall_stats and overall_stats.total_attempts and overall_stats.total_attempts > 0:
        dashboard_data.practice_performance_summary.total_sessions_completed = overall_stats.total_sessions
        dashboard_data.practice_performance_summary.total_questions_attempted = overall_stats.total_attempts
        # 直接使用 AVG 计算准确率
        # dashboard_data.practice_performance_summary.overall_accuracy = round(overall_stats.average_score, 1) if overall_stats.average_score is not None else None
        # 或者按答对题目数计算
        dashboard_data.practice_performance_summary.overall_accuracy = round(
            (overall_stats.correct_answers / overall_stats.total_attempts) * 100, 1
        )
        dashboard_data.core_metrics.overall_accuracy = dashboard_data.practice_performance_summary.overall_accuracy


    # 获取最近 5 次练习的分数
    recent_scores_stmt = (
        select(
            models.PracticeSession.id,
            models.PracticeSession.score,
            models.PracticeSession.completed_at
        )
        .filter(models.PracticeSession.user_id == user_id, models.PracticeSession.status == 'completed')
        .order_by(desc(models.PracticeSession.completed_at))
        .limit(5)
    )
    recent_scores_result = await db.execute(recent_scores_stmt)
    dashboard_data.practice_performance_summary.recent_session_scores = [
        {"session_id": r.id, "score": r.score, "completed_at": r.completed_at}
        for r in recent_scores_result.all() if r.score is not None
    ]

    # b. 按模块表现
    stmt_by_module = (
        select(
            models.PracticeModule.id.label("module_id"),
            models.PracticeModule.title.label("module_title"),
            func.count(models.PracticeSession.id).label("sessions_completed"),
            # func.sum(case((models.PracticeAttempt.is_correct == True, 1), else_=0)).label("correct_answers"),
            # func.count(models.PracticeAttempt.id).label("total_attempts"),
            func.avg(models.PracticeSession.score).label("average_module_score") # 按模块计算平均分
        )
        .select_from(models.PracticeModule)
        .join(models.PracticeSession, models.PracticeModule.id == models.PracticeSession.module_id)
        # .outerjoin(models.PracticeAttempt, models.PracticeSession.id == models.PracticeAttempt.session_id) # 不需要 join attempt
        .filter(models.PracticeSession.user_id == user_id, models.PracticeSession.status == 'completed')
        .group_by(models.PracticeModule.id, models.PracticeModule.title)
        .order_by(desc(func.avg(models.PracticeSession.score))) # 按平均分降序
    )
    by_module_result = await db.execute(stmt_by_module)
    dashboard_data.practice_performance_by_module = [
        ai_schemas.PracticeModulePerformance(
            module_id=row.module_id,
            module_title=row.module_title,
            sessions_completed=row.sessions_completed,
            accuracy=round(row.average_module_score, 1) if row.average_module_score is not None else None
        )
        for row in by_module_result.all()
    ]


    # --- 5. 错题本分析 ---
    stmt_mistake_status = (
        select(
            models.MistakeNotebookEntry.status,
            func.count(models.MistakeNotebookEntry.id).label("count")
        )
        .filter(models.MistakeNotebookEntry.user_id == user_id)
        .group_by(models.MistakeNotebookEntry.status)
    )
    mistake_status_result = await db.execute(stmt_mistake_status)
    total_mistakes = 0
    new_mistakes = 0
    reviewed_mistakes = 0
    for row in mistake_status_result.all():
        count = row.count or 0
        if row.status == 'new':
            dashboard_data.mistake_analysis_summary.new_mistakes = count
            new_mistakes = count
        elif row.status == 'reviewed':
            dashboard_data.mistake_analysis_summary.reviewed_mistakes = count
            reviewed_mistakes = count
        elif row.status == 'mastered':
            dashboard_data.mistake_analysis_summary.mastered_mistakes = count
        total_mistakes += count
    dashboard_data.mistake_analysis_summary.total_mistakes = total_mistakes
    dashboard_data.core_metrics.pending_mistakes = new_mistakes + reviewed_mistakes

    # 按模块统计错题
    stmt_mistake_by_module = (
        select(
            models.PracticeModule.id.label("module_id"),
            models.PracticeModule.title.label("module_title"),
            func.count(models.MistakeNotebookEntry.id).label("mistake_count")
        )
        .select_from(models.MistakeNotebookEntry)
        .join(models.PracticeQuestion, models.MistakeNotebookEntry.question_id == models.PracticeQuestion.id)
        .join(models.PracticeModule, models.PracticeQuestion.module_id == models.PracticeModule.id)
        .filter(models.MistakeNotebookEntry.user_id == user_id)
        .group_by(models.PracticeModule.id, models.PracticeModule.title)
        .order_by(desc(func.count(models.MistakeNotebookEntry.id)))
        .limit(5) # 显示错题最多的 5 个模块
    )
    mistake_by_module_result = await db.execute(stmt_mistake_by_module)
    dashboard_data.mistake_analysis_summary.top_mistake_modules = [
        {"module_id": row.module_id, "module_title": row.module_title, "count": row.mistake_count}
        for row in mistake_by_module_result.all()
    ]

    # 按知识点统计错题 (更复杂，需要 join knowledge_points)
    stmt_mistake_by_kp = (
        select(
            models.KnowledgePoint.id.label("kp_id"),
            models.KnowledgePoint.name.label("kp_name"),
            func.count(models.MistakeNotebookEntry.id).label("mistake_count")
        )
        .select_from(models.MistakeNotebookEntry)
        .join(models.PracticeQuestion, models.MistakeNotebookEntry.question_id == models.PracticeQuestion.id)
        .join(models.QuestionKnowledgePoint, models.PracticeQuestion.id == models.QuestionKnowledgePoint.question_id)
        .join(models.KnowledgePoint, models.QuestionKnowledgePoint.knowledge_point_id == models.KnowledgePoint.id)
        .filter(models.MistakeNotebookEntry.user_id == user_id)
        .group_by(models.KnowledgePoint.id, models.KnowledgePoint.name)
        .order_by(desc(func.count(models.MistakeNotebookEntry.id)))
        .limit(5) # 显示错题最多的 5 个知识点
    )
    mistake_by_kp_result = await db.execute(stmt_mistake_by_kp)
    dashboard_data.mistake_analysis_summary.top_mistake_knowledge_points = [
        {"kp_id": row.kp_id, "kp_name": row.kp_name, "count": row.mistake_count}
        for row in mistake_by_kp_result.all()
    ]


    # --- 6. 获取活跃的学习推荐 ---
    # 理想情况下，推荐是异步生成的，这里只负责读取
    # 为演示，先调用生成逻辑 (这会增加 API 响应时间)
    try:
        await recommendation_service.generate_and_store_recommendations(db, user_id=user_id) #
    except Exception as e:
         print(f"Error generating recommendations during dashboard fetch for user {user_id}: {e}")
         # 不应阻塞 Dashboard 返回，记录错误即可

    recommendations = await crud.recommendation.get_multi_by_user(
        db, user_id=user_id, status='active', limit=5 # 获取最多 5 条活跃推荐
    )
    dashboard_data.active_recommendations = recommendations
    dashboard_data.core_metrics.active_recommendations = len(recommendations)


    return dashboard_data

# --- recommendation_service.py 导入 ---
# 确保在 services/ai_analysis_service.py 中导入了 recommendation_service
# from app.services import recommendation_service # Add this import