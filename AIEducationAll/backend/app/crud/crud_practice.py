# AIEducationAll/backend/app/crud/crud_practice.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional
from datetime import datetime, timezone

from app.crud.base import CRUDBase
from app.models import (
    PracticeModule, PracticeQuestion, PracticeAnswer,
    PracticeSession, PracticeAttempt
)
from app.schemas import practice as practice_schemas  # Alias to avoid name conflicts
from .crud_mistake_notebook import mistake_notebook_entry #


# --- CRUD for PracticeModule ---
class CRUDPracticeModule(
    CRUDBase[PracticeModule, practice_schemas.PracticeModuleCreate, practice_schemas.PracticeModuleUpdate]):
    async def get_multi_with_details(
            self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[PracticeModule]:
        # Example: fetch modules and maybe count of questions later
        result = await db.execute(
            select(self.model)
            .order_by(self.model.id)
            .offset(skip)
            .limit(limit)
            # Add options here if you need related data like course title or question count
            # .options(joinedload(self.model.course))
        )
        return result.scalars().all()


# --- CRUD for PracticeQuestion ---
class CRUDPracticeQuestion(
    CRUDBase[PracticeQuestion, practice_schemas.PracticeQuestionCreate, practice_schemas.PracticeQuestionUpdate]):

    async def create_with_answers(self, db: AsyncSession, *,
                                  obj_in: practice_schemas.PracticeQuestionCreate) -> PracticeQuestion:
        """ Creates a question and optionally its answers (for MCQ). """
        answers_data = obj_in.answers or []
        # Pydantic V2: model_dump; V1: dict
        question_data = obj_in.model_dump(exclude={'answers'})
        # question_data = obj_in.dict(exclude={'answers'}) # V1

        db_question = PracticeQuestion(**question_data)
        db.add(db_question)
        await db.flush()  # Flush to get the question ID

        db_answers = []
        for answer_in in answers_data:
            answer_data = answer_in.model_dump()
            # answer_data = answer_in.dict() # V1
            # Ensure question_id is set if not provided in answer_in
            answer_data['question_id'] = db_question.id
            db_answer = PracticeAnswer(**answer_data)
            db_answers.append(db_answer)

        if db_answers:
            db.add_all(db_answers)
            await db.flush()

        # Optionally refresh the question to load the answers relationship
        # await db.refresh(db_question, attribute_names=['answers'])
        return db_question

    async def get_questions_for_module(
            self, db: AsyncSession, *, module_id: int, load_answers: bool = True
    ) -> List[PracticeQuestion]:
        """ Gets all questions for a specific module, optionally loading answers. """
        stmt = (
            select(self.model)
            .filter(self.model.module_id == module_id)
            .order_by(self.model.id)  # Or difficulty, or a specific order
        )
        if load_answers:
            stmt = stmt.options(
                selectinload(self.model.answers)  # 仅指定预加载答案
            )
        result = await db.execute(stmt)
        return result.scalars().unique().all()  # Use unique() because of one-to-many load


# --- CRUD for PracticeAnswer ---
# Basic CRUD from base might suffice, or add specific methods if needed
class CRUDPracticeAnswer(
    CRUDBase[PracticeAnswer, practice_schemas.PracticeAnswerCreate, practice_schemas.PracticeAnswerUpdate]):
    pass


# --- CRUD for PracticeSession ---
class CRUDPracticeSession(
    CRUDBase[PracticeSession, practice_schemas.PracticeSessionCreate, practice_schemas.PracticeSessionUpdate]):
    async def create_session(self, db: AsyncSession, *, user_id: int, module_id: int) -> PracticeSession:
        """ Starts a new practice session for a user and module. """
        # Check if module exists (optional, handled by FK constraint mostly)
        # module = await db.get(PracticeModule, module_id)
        # if not module: ... raise error ...

        db_obj = PracticeSession(user_id=user_id, module_id=module_id, status='in_progress')
        db.add(db_obj)
        await db.flush()
        return db_obj

    async def get_session_with_results(self, db: AsyncSession, *, session_id: int, user_id: int) -> Optional[
        PracticeSession]:
        """ 获取会话及其尝试，包括问题详情和答案 (答案排序由模型关系定义)。 """
        result = await db.execute(
            select(PracticeSession)
            .where(PracticeSession.id == session_id, PracticeSession.user_id == user_id)
            .options(
                selectinload(PracticeSession.attempts)
                .options(
                    # 加载尝试关联的问题
                    joinedload(PracticeAttempt.question)
                    # 加载该问题的答案 (现在会自动按 display_order, id 排序)
                    .selectinload(PracticeQuestion.answers), # <--- 现在无需在此处排序
                    # 加载用户选择的答案 (如果是选择题)
                    joinedload(PracticeAttempt.selected_answer)
                )
                # .order_by(PracticeAttempt.submitted_at)  # 按提交时间排序尝试记录
            )
            .options(joinedload(PracticeSession.module))  # 加载模块详情
        )
        return result.scalars().first()

    async def complete_session(self, db: AsyncSession, *, session: PracticeSession, score: float) -> PracticeSession:
        """ Marks a session as completed and saves the score. """
        session.completed_at = datetime.now(timezone.utc)
        session.status = 'completed'
        session.score = score
        db.add(session)
        await db.flush()
        # await db.refresh(session) # Optional
        return session


# --- CRUD for PracticeAttempt ---
# Needs more specific methods than basic CRUD
class CRUDPracticeAttempt:  # Not inheriting from CRUDBase directly here

    async def create_attempt(self, db: AsyncSession, *, session_id: int,
                             obj_in: practice_schemas.PracticeAttemptSubmit) -> PracticeAttempt:
        """ Creates a single attempt record within a session. Grading happens separately. """
        # Pydantic V2: model_dump; V1: dict
        attempt_data = obj_in.model_dump()
        # attempt_data = obj_in.dict() # V1
        attempt_data['session_id'] = session_id
        # is_correct will be determined later during submission/grading
        attempt_data['is_correct'] = None

        db_obj = PracticeAttempt(**attempt_data)
        db.add(db_obj)
        await db.flush()
        return db_obj

    async def submit_attempts(
            self,
            db: AsyncSession,
            *,
            session_id: int,
            user_id: int,  # <-- 新增参数：需要知道是哪个用户提交的
            attempts_in: List[practice_schemas.PracticeAttemptSubmit]
    ) -> List[PracticeAttempt]:
        """
        提交指定会话的多个答题尝试。
        包含基础的评分逻辑 (目前仅限选择题) 并自动将错误题目添加到错题本。
        """
        created_attempts = []
        question_ids = [a.question_id for a in attempts_in]

        # 1. 批量获取问题及其正确答案
        correct_answers_map = {}  # {question_id: correct_answer_id}
        questions = await db.execute(
            select(PracticeQuestion)
            .options(selectinload(
                PracticeQuestion.answers.and_(PracticeAnswer.is_correct == True)))  # 仅加载正确答案
            .filter(PracticeQuestion.id.in_(question_ids))
        )
        # --- 修改：在循环外获取一次问题列表 ---
        questions_list = questions.scalars().unique().all()
        # --- 结束修改 ---
        for q in questions_list:  # 使用获取到的列表
            if q.question_type == 'multiple_choice' and q.answers:
                correct_answers_map[q.id] = q.answers[0].id
            # 可以为其他题型添加正确答案获取逻辑

        # --- 新增：用于收集做错的题目ID ---
        incorrect_question_ids = set()
        # --- 结束新增 ---

        # 2. 创建尝试记录并进行评分
        for attempt_in in attempts_in:
            attempt_data = attempt_in.model_dump()  # Pydantic V2
            # attempt_data = attempt_in.dict() # Pydantic V1
            attempt_data['session_id'] = session_id
            attempt_data['submitted_at'] = datetime.now(timezone.utc)

            # 简单选择题评分
            is_correct = None
            correct_answer_id = correct_answers_map.get(attempt_in.question_id)
            if correct_answer_id is not None and attempt_in.selected_answer_id is not None:
                is_correct = (attempt_in.selected_answer_id == correct_answer_id)
            # 其他题型占位符 (例如填空题、编程题)
            elif attempt_in.user_answer_text is not None:
                # 实际应用中需要更复杂的评分逻辑
                # 这里暂时假设文本题都未评分或需要手动评分
                is_correct = None  # 或 False

            attempt_data['is_correct'] = is_correct

            # --- 新增：如果回答错误，记录题目 ID ---
            if is_correct is False:  # 明确回答错误才记录
                incorrect_question_ids.add(attempt_in.question_id)
            # --- 结束新增 ---

            db_obj = PracticeAttempt(**attempt_data)
            db.add(db_obj)
            created_attempts.append(db_obj)

        await db.flush()  # 保存所有尝试记录

        # --- 新增：将所有做错的题目添加到错题本 ---
        if incorrect_question_ids:
            print(f"用户 {user_id} 在会话 {session_id} 中答错了题目: {incorrect_question_ids}")
            for q_id in incorrect_question_ids:
                # 调用错题本 CRUD 添加条目
                # 注意：add_entry 内部会处理重复添加的情况
                added_mistake = await mistake_notebook_entry.add_entry(  #
                    db=db, user_id=user_id, question_id=q_id
                )
                if added_mistake:
                    print(f"题目 {q_id} 已添加到用户 {user_id} 的错题本。")
            # 注意：这里没有立即 commit，依赖于 FastAPI 的数据库会话管理
        # --- 结束新增 ---

        return created_attempts  # 返回创建的尝试记录

    async def calculate_session_score(self, db: AsyncSession, *, session_id: int) -> float:
        # ... (此函数不变) ...
        result = await db.execute(
            select(PracticeAttempt)
            .where(PracticeAttempt.session_id == session_id)
        )
        attempts = result.scalars().all()
        if not attempts:
            return 0.0

        correct_count = sum(1 for attempt in attempts if attempt.is_correct is True)
        total_questions_attempted = len(attempts)

        score = (correct_count / total_questions_attempted) * 100 if total_questions_attempted > 0 else 0
        return round(score, 2)


# Instantiate CRUD objects
practice_module = CRUDPracticeModule(PracticeModule)
practice_question = CRUDPracticeQuestion(PracticeQuestion)
practice_answer = CRUDPracticeAnswer(PracticeAnswer)
practice_session = CRUDPracticeSession(PracticeSession)
practice_attempt = CRUDPracticeAttempt()  # Using class with static-like methods
