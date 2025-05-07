# app/models/__init__.py
from app.db.base_class import Base
from .user import User
from .password_reset_token import PasswordResetToken
from .course import Course
from .lesson import Lesson
from .enrollment import Enrollment
from .progress import Progress
# --- Add Practice Models ---
from .practice_module import PracticeModule
from .practice_question import PracticeQuestion
from .practice_answer import PracticeAnswer
from .practice_session import PracticeSession
from .practice_attempt import PracticeAttempt
from .mistake_notebook_entry import MistakeNotebookEntry
from .knowledge_point import KnowledgePoint, QuestionKnowledgePoint
from .recommendation import Recommendation

# --- End Add ---