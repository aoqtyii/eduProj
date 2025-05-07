# AIEducationAll/backend/app/api/endpoints/practice.py
from fastapi import APIRouter, Depends, HTTPException, status, Body, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


# --- Practice Module Endpoints ---

@router.get("/modules/", response_model=List[schemas.PracticeModule])
async def read_practice_modules(
        db: AsyncSession = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        # current_user: models.User = Depends(deps.get_current_active_user) # Uncomment if listing needs auth
):
    """
    获取可用的练习模块列表。
    """
    modules = await crud.practice_module.get_multi(db, skip=skip, limit=limit)
    # Consider adding course title or other details if needed via get_multi_with_details
    return modules


@router.get("/modules/{module_id}/questions", response_model=List[schemas.PracticeQuestionWithOptions])
async def read_module_questions(
        module_id: int,
        db: AsyncSession = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)  # Requires login to view questions
):
    """
    获取指定练习模块的所有问题及其选项（如果是选择题）。
    """
    module = await crud.practice_module.get(db, id=module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"练习模块 {module_id} 未找到。")

    questions = await crud.practice_question.get_questions_for_module(db, module_id=module_id, load_answers=True)
    return questions


# --- Practice Session Endpoints ---

@router.post("/sessions/", response_model=schemas.PracticeSession, status_code=status.HTTP_201_CREATED)
async def start_practice_session(
        *,
        db: AsyncSession = Depends(deps.get_db),
        session_in: schemas.PracticeSessionCreate,  # Expects {"module_id": N}
        current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    为当前用户和指定模块开始一个新的练习会话。
    """
    # 检查模块是否存在
    module = await crud.practice_module.get(db, id=session_in.module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"练习模块 {session_in.module_id} 未找到，无法开始会话。"
        )

    # 创建会话
    session = await crud.practice_session.create_session(
        db=db, user_id=current_user.id, module_id=session_in.module_id
    )
    return session


@router.post("/sessions/{session_id}/submit", response_model=schemas.PracticeSessionResult)
async def submit_practice_session_answers(
        *,
        session_id: int,
        db: AsyncSession = Depends(deps.get_db),
        attempts_in: List[schemas.PracticeAttemptSubmit] = Body(...),  # List of answers submitted
        current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    提交指定练习会话的所有答案。
    后端将进行评分（目前仅限选择题），计算总分，并将会话标记为完成。
    """
    # 1. 获取会话并验证用户和状态
    session = await crud.practice_session.get(db, id=session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="练习会话未找到。")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此练习会话。")
    if session.status == 'completed':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="此练习会话已完成，无法重复提交。")

    # 2. (可选) 验证提交的题目是否属于该会话的模块
    # module = await crud.practice_module.get(db, id=session.module_id)
    # module_question_ids = {q.id for q in module.questions} # Requires loading questions relationship
    # submitted_question_ids = {a.question_id for a in attempts_in}
    # if not submitted_question_ids.issubset(module_question_ids):
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="提交包含无效问题ID。")

    # 3. 创建答题记录并进行初步评分
    await crud.practice_attempt.submit_attempts(
        db=db,
        session_id=session_id,
        user_id=current_user.id,  # <--- 传递当前用户 ID
        attempts_in=attempts_in
    )  #

    # 4. 计算最终得分
    final_score = await crud.practice_attempt.calculate_session_score(db=db, session_id=session_id)

    # 5. 更新会话状态和分数
    await crud.practice_session.complete_session(db=db, session=session, score=final_score)

    # 6. 获取包含完整结果的会话数据并返回
    session_with_results = await crud.practice_session.get_session_with_results(db=db, session_id=session_id,
                                                                                user_id=current_user.id)
    if not session_with_results:
        # 这理论上不应该发生，因为我们刚刚更新了它
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="无法检索会话结果。")

    return session_with_results


@router.get("/sessions/{session_id}/results", response_model=schemas.PracticeSessionResult)
async def get_practice_session_results(
        session_id: int,
        db: AsyncSession = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    获取指定已完成练习会话的结果，包括所有答题尝试、问题详情和正确答案。
    """
    session_with_results = await crud.practice_session.get_session_with_results(db=db, session_id=session_id,
                                                                                user_id=current_user.id)

    if not session_with_results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="练习会话结果未找到或无权访问。")

    # 可以选择性地检查会话是否已完成
    # if session_with_results.status != 'completed':
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="会话尚未完成。")

    return session_with_results


# 你还可以添加管理端点，例如：
# - POST /modules/ : 创建练习模块 (管理员/教师)
# - POST /questions/ : 创建练习题目 (管理员/教师)
# - PUT /modules/{module_id} : 更新模块
# - PUT /questions/{question_id} : 更新题目
# 等等...
# =============================================
# Admin Endpoints (新添加的管理端点)
# =============================================

# --- Practice Module Admin Endpoints ---

@router.post("/admin/modules/", response_model=schemas.PracticeModule, status_code=status.HTTP_201_CREATED)
async def create_practice_module(
        *,
        db: AsyncSession = Depends(deps.get_db),
        module_in: schemas.PracticeModuleCreate,
        current_user: models.User = Depends(deps.get_current_active_superuser)  # 需要超级用户权限
):
    """
    [Admin] 创建一个新的练习模块。
    """
    # 可选：检查关联的 course_id 是否存在
    if module_in.course_id:
        course = await crud.course.get(db, id=module_in.course_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"课程 {module_in.course_id} 未找到。")

    module = await crud.practice_module.create(db=db, obj_in=module_in)
    return module


@router.put("/admin/modules/{module_id}", response_model=schemas.PracticeModule)
async def update_practice_module(
        *,
        db: AsyncSession = Depends(deps.get_db),
        module_id: int,
        module_in: schemas.PracticeModuleUpdate,
        current_user: models.User = Depends(deps.get_current_active_superuser)  # 需要超级用户权限
):
    """
    [Admin] 更新一个练习模块。
    """
    module = await crud.practice_module.get(db, id=module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="练习模块未找到。")

    # 可选：检查更新的 course_id 是否存在
    if module_in.course_id is not None:  # Check if course_id is explicitly provided in update
        if module_in.course_id > 0:  # Assuming 0 or negative means detach
            course = await crud.course.get(db, id=module_in.course_id)
            if not course:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"课程 {module_in.course_id} 未找到。")
        # Allow setting course_id to null if needed, assuming model allows it

    updated_module = await crud.practice_module.update(db=db, db_obj=module, obj_in=module_in)
    return updated_module


@router.delete("/admin/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_practice_module(
        *,
        db: AsyncSession = Depends(deps.get_db),
        module_id: int,
        current_user: models.User = Depends(deps.get_current_active_superuser)  # 需要超级用户权限
):
    """
    [Admin] 删除一个练习模块及其所有关联的问题和会话（通过级联删除）。
    """
    module = await crud.practice_module.get(db, id=module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="练习模块未找到。")

    await crud.practice_module.remove(db=db, id=module_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Practice Question Admin Endpoints ---

@router.post("/admin/questions/", response_model=schemas.PracticeQuestion, status_code=status.HTTP_201_CREATED)
async def create_practice_question(
        *,
        db: AsyncSession = Depends(deps.get_db),
        question_in: schemas.PracticeQuestionCreate,
        current_user: models.User = Depends(deps.get_current_active_superuser)  # 需要超级用户权限
):
    """
    [Admin] 创建一个新的练习题目，可以同时创建其答案选项（如果是选择题）。
    """
    # 检查关联的 module_id 是否存在
    module = await crud.practice_module.get(db, id=question_in.module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"练习模块 {question_in.module_id} 未找到。")

    # 验证：如果是多选题，必须提供答案且至少有一个是正确的
    if question_in.question_type == 'multiple_choice':
        if not question_in.answers:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="选择题必须包含答案选项。")
        if not any(ans.is_correct for ans in question_in.answers):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="选择题必须至少有一个正确答案。")
        # 可以添加更多验证，例如不允许所有选项都正确

    question = await crud.practice_question.create_with_answers(db=db, obj_in=question_in)
    # 返回包含答案的完整问题信息
    # 需要重新获取或确保 create_with_answers 返回包含答案的对象
    # 为了简单起见，这里只返回基本问题信息，如果需要答案，客户端可以单独请求
    return question  # 可能需要调整 schemas.PracticeQuestion 的定义或使用 PracticeQuestionWithOptions


@router.put("/admin/questions/{question_id}",
            response_model=schemas.PracticeQuestion)  # 可能需要 PracticeQuestionWithOptions
async def update_practice_question(
        *,
        db: AsyncSession = Depends(deps.get_db),
        question_id: int,
        question_in: schemas.PracticeQuestionUpdate,
        current_user: models.User = Depends(deps.get_current_active_superuser)  # 需要超级用户权限
):
    """
    [Admin] 更新一个练习题目。
    注意：更新答案选项通常需要单独的端点或更复杂的逻辑。
    """
    question = await crud.practice_question.get(db, id=question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="练习题目未找到。")

    # 注意：这个更新目前不处理答案选项的更新。
    # 如果需要更新答案，建议要么：
    # 1. 提供单独的 PUT /admin/answers/{answer_id} 端点。
    # 2. 在此端点中接受答案列表，并执行删除旧答案、添加新答案的逻辑。
    updated_question = await crud.practice_question.update(db=db, db_obj=question, obj_in=question_in)
    return updated_question


@router.delete("/admin/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_practice_question(
        *,
        db: AsyncSession = Depends(deps.get_db),
        question_id: int,
        current_user: models.User = Depends(deps.get_current_active_superuser)  # 需要超级用户权限
):
    """
    [Admin] 删除一个练习题目及其所有关联的答案和尝试记录（通过级联删除）。
    """
    question = await crud.practice_question.get(db, id=question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="练习题目未找到。")

    await crud.practice_question.remove(db=db, id=question_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
