# 文件: AIEducationAll/backend/app/api/endpoints/mistake_notebook.py

from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

# --- 添加错题条目 (通常由系统自动完成，但提供手动接口可能有用) ---
# 注意：这里假设手动添加，更好的方式是在提交练习答案时自动添加
@router.post(
    "/question/{question_id}",
    response_model=schemas.MistakeNotebookEntryPublic,
    status_code=status.HTTP_201_CREATED,
    summary="手动将题目添加到错题本"
)
async def add_mistake_entry_manually(
    *,
    db: AsyncSession = Depends(deps.get_db),
    question_id: int,
    notes_in: Optional[schemas.MistakeNotebookEntryUpdate] = None, # 可选，用于添加笔记
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    将指定的练习题目添加到当前用户的错题本。
    如果题目已存在于错题本中，则可能不执行任何操作或返回现有条目 (取决于 CRUD 实现)。
    """
    entry_notes = notes_in.notes if notes_in else None
    entry = await crud.mistake_notebook_entry.add_entry(
        db=db, user_id=current_user.id, question_id=question_id, notes=entry_notes
    )

    if not entry:
        # 可能因为题目不存在，或题目已在错题本中 (根据 add_entry 实现决定如何处理)
        # 需要检查题目是否存在
        question = await db.get(models.PracticeQuestion, question_id)
        if not question:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"题目 ID {question_id} 不存在")
        # 如果题目存在但 entry 为 None，说明已存在于错题本
        # 可以选择返回 409 Conflict 或查找并返回现有条目
        existing_entry = await db.execute(
             select(models.MistakeNotebookEntry).filter_by(user_id=current_user.id, question_id=question_id)
             .options(selectinload(models.MistakeNotebookEntry.question).selectinload(models.PracticeQuestion.answers))
        )
        existing_entry_obj = existing_entry.scalars().first()
        if existing_entry_obj:
            return existing_entry_obj # 返回已存在的条目
        else:
             # 理论上不应发生这种情况，除非 add_entry 中有其他逻辑返回 None
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="无法添加错题条目")


    # 需要重新加载包含题目信息的条目以匹配 response_model
    # (或者修改 add_entry 返回包含预加载信息的对象)
    refreshed_entry = await db.execute(
        select(models.MistakeNotebookEntry)
        .options(selectinload(models.MistakeNotebookEntry.question).selectinload(models.PracticeQuestion.answers))
        .filter(models.MistakeNotebookEntry.id == entry.id)
    )
    entry_with_details = refreshed_entry.scalars().first()

    return entry_with_details

# --- 获取当前用户的错题列表 ---
@router.get(
    "/",
    response_model=List[schemas.MistakeNotebookEntryPublic],
    summary="获取当前用户的错题本列表"
)
async def read_my_mistake_entries(
    *,
    db: AsyncSession = Depends(deps.get_db),
    status: Optional[str] = Query(None, description="按状态过滤 (e.g., 'new', 'reviewed', 'mastered')"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    获取当前用户的错题本条目，支持按状态过滤和分页。
    返回结果包含完整的题目信息及选项。
    """
    entries = await crud.mistake_notebook_entry.get_entries_by_user(
        db=db, user_id=current_user.id, status=status, skip=skip, limit=limit
    )
    # CRUD 函数已经处理了预加载
    return entries

# --- 更新错题条目状态或笔记 ---
@router.put(
    "/entry/{entry_id}",
    response_model=schemas.MistakeNotebookEntryPublic,
    summary="更新错题条目的状态或笔记"
)
async def update_mistake_entry(
    *,
    db: AsyncSession = Depends(deps.get_db),
    entry_id: int,
    entry_in: schemas.MistakeNotebookEntryUpdate, # 请求体包含 status?, notes?, last_reviewed_at?
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    更新指定 ID 的错题条目的状态 (如 'reviewed', 'mastered') 或用户笔记。
    只能更新属于自己的错题。
    """
    db_entry = await crud.mistake_notebook_entry.get_entry_by_id_and_user(
         db=db, entry_id=entry_id, user_id=current_user.id
    )
    if not db_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="错题条目未找到或无权访问")

    updated_entry = await crud.mistake_notebook_entry.update_entry(
        db=db, db_obj=db_entry, obj_in=entry_in
    )

    # 同样需要重新加载关联信息
    refreshed_entry = await db.execute(
        select(models.MistakeNotebookEntry)
        .options(selectinload(models.MistakeNotebookEntry.question).selectinload(models.PracticeQuestion.answers))
        .filter(models.MistakeNotebookEntry.id == updated_entry.id)
    )
    entry_with_details = refreshed_entry.scalars().first()

    return entry_with_details

# --- 从错题本删除条目 ---
@router.delete(
    "/entry/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="从错题本删除一个条目"
)
async def delete_mistake_entry(
    *,
    db: AsyncSession = Depends(deps.get_db),
    entry_id: int,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    从当前用户的错题本中删除指定 ID 的条目。
    """
    deleted_entry = await crud.mistake_notebook_entry.remove_entry(
        db=db, entry_id=entry_id, user_id=current_user.id
    )
    if not deleted_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="错题条目未找到或无权访问")

    return Response(status_code=status.HTTP_204_NO_CONTENT)