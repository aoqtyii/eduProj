# app/schemas/__init__.py

# --- 基础模型 Schemas ---
from .user import User, UserCreate, UserRegister, UserUpdate, UserInDB
from .course import Course, CourseCreate, CourseUpdate, CourseInDB, CourseBasic
from .lesson import Lesson, LessonCreate, LessonUpdate, LessonInDB
from .enrollment import Enrollment, EnrollmentCreate, EnrollmentPublic
from .progress import Progress, ProgressCreate, ProgressUpdate
from .practice import (
    PracticeAnswer, PracticeAnswerCreate, PracticeAnswerUpdate,
    PracticeQuestion, PracticeQuestionCreate, PracticeQuestionUpdate, PracticeQuestionWithOptions,
    PracticeModule, PracticeModuleCreate, PracticeModuleUpdate,
    PracticeSession, PracticeSessionCreate, PracticeSessionUpdate, PracticeSessionResult,
    PracticeAttemptSubmit, PracticeAttemptResult
)
from .mistake_notebook import (
    MistakeNotebookEntry,
    MistakeNotebookEntryCreate,
    MistakeNotebookEntryUpdate,
    MistakeNotebookEntryPublic
)
from .knowledge_point import KnowledgePoint, KnowledgePointCreate
from .recommendation import Recommendation, RecommendationCreate, RecommendationUpdate

# --- !! 修正这里的导入名称 !! ---
from .ai_analysis import StudentAIDashboardData # <-- 已修正为 StudentAIDashboardData

# --- 其他辅助/认证 Schemas ---
from .token import Token, TokenPayload
from .password import PasswordResetRequest, ForgotPasswordRequest