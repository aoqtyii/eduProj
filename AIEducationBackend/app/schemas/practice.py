# AIEducationAll/backend/app/schemas/practice.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# --- Practice Answer Schemas ---

class PracticeAnswerBase(BaseModel):
    answer_text: str
    is_correct: bool = False
    display_order: Optional[int] = 0


class PracticeAnswerCreate(PracticeAnswerBase):
    question_id: int  # Need question id when creating


class PracticeAnswerUpdate(BaseModel):
    answer_text: Optional[str] = None
    is_correct: Optional[bool] = None
    display_order: Optional[int] = None


class PracticeAnswer(PracticeAnswerBase):
    id: int
    question_id: int

    class Config:
        from_attributes = True


# --- Practice Question Schemas ---

class PracticeQuestionBase(BaseModel):
    question_text: str
    question_type: str = Field(..., example="multiple_choice")  # e.g., 'multiple_choice', 'coding', 'fill_in_blank'
    difficulty: Optional[int] = 1
    hints: Optional[str] = None
    explanation: Optional[str] = None


class PracticeQuestionCreate(PracticeQuestionBase):
    module_id: int
    # For multiple choice, answers might be created separately or included here
    answers: Optional[List[PracticeAnswerCreate]] = []  # Allow creating answers along with question


class PracticeQuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    question_type: Optional[str] = None
    difficulty: Optional[int] = None
    hints: Optional[str] = None
    explanation: Optional[str] = None
    # module_id is generally not updated


# Schema for returning a question WITH its potential answers (for display in frontend)
class PracticeQuestionWithOptions(PracticeQuestionBase):
    id: int
    module_id: int
    answers: List[PracticeAnswer] = []  # Include answers for MCQs

    class Config:
        from_attributes = True


class PracticeQuestion(PracticeQuestionBase):  # Basic question schema (e.g., for listing)
    id: int
    module_id: int

    class Config:
        from_attributes = True


# --- Practice Module Schemas ---

class PracticeModuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    course_id: Optional[int] = None  # Optional link to course


class PracticeModuleCreate(PracticeModuleBase):
    pass  # Base fields are sufficient for creation


class PracticeModuleUpdate(PracticeModuleBase):
    title: Optional[str] = None  # Allow optional updates
    description: Optional[str] = None
    course_id: Optional[int] = None


class PracticeModule(PracticeModuleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    # Optionally include questions count or basic info if needed often
    # questions_count: Optional[int] = None

    class Config:
        from_attributes = True


# --- Practice Session Schemas ---

class PracticeSessionBase(BaseModel):
    module_id: int
    # user_id is inferred from the logged-in user


class PracticeSessionCreate(PracticeSessionBase):
    pass  # module_id is enough to start


class PracticeSessionUpdate(BaseModel):
    # Typically only status and score are updated upon completion
    status: Optional[str] = None  # e.g., 'completed'
    score: Optional[float] = None
    completed_at: Optional[datetime] = None


class PracticeSession(PracticeSessionBase):
    id: int
    user_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    status: str

    class Config:
        from_attributes = True


# --- Practice Attempt Schemas ---

# Schema for submitting an answer
class PracticeAttemptSubmit(BaseModel):
    question_id: int
    selected_answer_id: Optional[int] = None  # For multiple choice
    user_answer_text: Optional[str] = None  # For text/coding answers


# Schema for representing an attempt's result (including feedback/explanation)
class PracticeAttemptResult(BaseModel):
    id: int
    question_id: int
    selected_answer_id: Optional[int] = None
    user_answer_text: Optional[str] = None
    is_correct: Optional[bool] = None
    submitted_at: datetime
    feedback: Optional[str] = None
    question: Optional[PracticeQuestionWithOptions] = None  # Include full question details for review

    class Config:
        from_attributes = True


class PracticeSessionResult(PracticeSession):  # Extends session details
    attempts: List[PracticeAttemptResult] = []
