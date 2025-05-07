# 文件: AIEducationAll/backend/app/crud/crud_mistake_notebook.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime, timezone

from app.crud.base import CRUDBase
from app.models import MistakeNotebookEntry, PracticeQuestion, PracticeAnswer # 需要导入模型
from app.schemas import MistakeNotebookEntryCreate, MistakeNotebookEntryUpdate # 需要导入模式

class CRUDMistakeNotebookEntry(CRUDBase[MistakeNotebookEntry, MistakeNotebookEntryCreate, MistakeNotebookEntryUpdate]):

    async def add_entry(
        self, db: AsyncSession, *, user_id: int, question_id: int, notes: Optional[str] = None
    ) -> Optional[MistakeNotebookEntry]:
        """
        向指定用户的错题本添加一个题目。
        如果条目已存在 (基于 user_id 和 question_id 的唯一约束)，则不执行任何操作或返回现有条目。
        """
        # 检查题目是否存在 (可选，但推荐)
        question = await db.get(PracticeQuestion, question_id)
        if not question:
            return None # 或者抛出异常

        # 创建新的错题条目对象
        db_obj = MistakeNotebookEntry(
            user_id=user_id,
            question_id=question_id,
            notes=notes,
            status='new', # 初始状态
            added_at=datetime.now(timezone.utc) # 显式设置添加时间
        )
        db.add(db_obj)
        try:
            await db.flush() # 尝试写入数据库
            # 可选：刷新以加载关系，但在此处可能不需要
            # await db.refresh(db_obj)
            return db_obj
        except IntegrityError: # 捕获违反唯一约束的错误
            await db.rollback() # 回滚事务
            print(f"Info: Mistake entry for user {user_id}, question {question_id} already exists.")
            # 可以选择查找并返回现有条目，或者简单返回 None 表示未新增
            # result = await db.execute(
            #     select(self.model).filter_by(user_id=user_id, question_id=question_id)
            # )
            # return result.scalars().first()
            return None # 或者返回已存在的条目


    async def get_entries_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[MistakeNotebookEntry]:
        """
        获取指定用户错题本中的条目列表，支持按状态过滤和分页。
        会预加载关联的题目信息及其答案。
        """
        stmt = (
            select(self.model)
            .filter(self.model.user_id == user_id)
            .options(
                # 预加载关联的 PracticeQuestion，并且也预加载该 Question 的 Answers
                selectinload(self.model.question)
                .selectinload(PracticeQuestion.answers) # 答案会根据模型定义排序
            )
            .order_by(self.model.added_at.desc()) # 按添加时间降序排序
            .offset(skip)
            .limit(limit)
        )

        # 如果提供了 status 参数，则添加过滤条件
        if status:
            stmt = stmt.filter(self.model.status == status)

        result = await db.execute(stmt)
        # 使用 unique() 因为嵌套的 selectinload 可能导致主对象重复
        return result.scalars().unique().all()

    async def get_entry_by_id_and_user(
        self, db: AsyncSession, *, entry_id: int, user_id: int
    ) -> Optional[MistakeNotebookEntry]:
         """ 获取用户拥有的特定错题条目 """
         result = await db.execute(
             select(self.model).filter(self.model.id == entry_id, self.model.user_id == user_id)
         )
         return result.scalars().first()


    async def update_entry(
        self,
        db: AsyncSession,
        *,
        db_obj: MistakeNotebookEntry, # 要更新的数据库对象
        obj_in: MistakeNotebookEntryUpdate # 包含更新数据的 Pydantic Schema
    ) -> MistakeNotebookEntry:
        """ 更新错题条目的状态、笔记或复习时间 """
        # 使用基类的 update 方法，它会处理 Pydantic 模型到字典的转换和字段更新
        # 如果要更新 last_reviewed_at，确保 obj_in 包含该字段
        if obj_in.status or obj_in.notes or obj_in.last_reviewed_at is not None:
             if obj_in.last_reviewed_at is None and obj_in.status == 'reviewed': # 自动设置复习时间
                  obj_in.last_reviewed_at = datetime.now(timezone.utc)

        return await super().update(db=db, db_obj=db_obj, obj_in=obj_in)

    async def remove_entry(
        self, db: AsyncSession, *, entry_id: int, user_id: int
    ) -> Optional[MistakeNotebookEntry]:
        """ 删除用户拥有的特定错题条目 """
        # 先获取对象以确认所有权
        db_obj = await self.get_entry_by_id_and_user(db=db, entry_id=entry_id, user_id=user_id)
        if db_obj:
            # 使用基类的 remove 方法通过 ID 删除
            # 注意：这里我们已经获取了对象，可以直接调用 db.delete(db_obj)
            await db.delete(db_obj)
            await db.flush()
            return db_obj # 返回被删除的对象 (或 True)
        return None # 如果未找到或不属于该用户，返回 None

# 实例化 CRUD 对象
mistake_notebook_entry = CRUDMistakeNotebookEntry(MistakeNotebookEntry)