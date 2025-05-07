# AIEducationAll/backend/app/schemas/ai_analysis.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from .recommendation import Recommendation  # Import Recommendation schema
from .practice import PracticeModule  # Import PracticeModule if needed for performance by module


# --- 复用或调整自 dashboard.py 的 Schema ---
class DashboardCourseProgress(BaseModel):
    course_id: int
    course_title: str
    total_lessons: int = 0
    completed_lessons: int = 0
    progress_percentage: int = 0
    last_accessed_at: Optional[datetime] = None  # 新增：上次访问时间


class DashboardRecentActivity(BaseModel):
    activity_type: str  # 'lesson_accessed', 'practice_completed', 'mistake_added', 'recommendation_received' etc.
    item_id: Optional[int] = None  # Might be lesson_id, session_id, question_id, recommendation_id
    item_title: str
    timestamp: datetime
    details: Optional[Dict] = None  # 存储额外信息，如练习分数, 推荐原因等


# --- 练习表现分析 Schema ---
class PracticePerformanceSummary(BaseModel):
    overall_accuracy: Optional[float] = Field(None, description="Overall accuracy percentage (0-100)")
    total_sessions_completed: int = 0
    total_questions_attempted: int = 0
    # 可以添加最近几次练习的分数趋势列表
    recent_session_scores: List[Dict] = Field([],
                                              description="List of recent scores, e.g., [{'session_id': 1, 'score': 85.0, 'completed_at': ...}]")


class PracticeModulePerformance(BaseModel):
    module_id: int
    module_title: str
    accuracy: Optional[float] = None
    sessions_completed: int = 0
    # questions_attempted: int = 0


# --- 错题本分析 Schema ---
class MistakeAnalysisSummary(BaseModel):
    total_mistakes: int = 0
    new_mistakes: int = 0
    reviewed_mistakes: int = 0
    mastered_mistakes: int = 0
    # 可以添加最常出错的知识点或模块列表
    top_mistake_modules: List[Dict] = Field([],
                                            description="Modules with the most mistakes, e.g., [{'module_id': 1, 'module_title': '...', 'count': 5}]")
    top_mistake_knowledge_points: List[Dict] = Field([],
                                                     description="Knowledge points with the most mistakes, e.g., [{'kp_id': 1, 'kp_name': '...', 'count': 3}]")


# --- 核心指标 Schema ---
class CoreMetrics(BaseModel):
    average_progress: int = 0
    overall_accuracy: Optional[float] = None
    pending_mistakes: int = 0  # new + reviewed
    active_recommendations: int = 0


# --- 主 Schema ---
class StudentAIDashboardData(BaseModel):  # 重命名以更清晰
    core_metrics: CoreMetrics
    ongoing_courses_progress: List[DashboardCourseProgress] = []  # 改名为进行中的课程
    recent_activity: List[DashboardRecentActivity] = []
    practice_performance_summary: PracticePerformanceSummary
    practice_performance_by_module: List[PracticeModulePerformance] = []  # 按模块分析
    mistake_analysis_summary: MistakeAnalysisSummary
    active_recommendations: List[Recommendation] = []  # 只展示活跃的推荐

    class Config:
        from_attributes = True  # Pydantic V2
        # orm_mode = True # Pydantic V1
