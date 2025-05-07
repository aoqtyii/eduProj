# 文件: AIEducationAll/backend/app/schemas/mistake_notebook.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# 导入练习题目的 Schema，以便在返回错题时嵌套题目信息
from .practice import PracticeQuestionWithOptions

# 基础模式，包含所有字段
class MistakeNotebookEntryBase(BaseModel):
    question_id: int
    status: str = 'new'
    notes: Optional[str] = None
    last_reviewed_at: Optional[datetime] = None

# 创建时需要的信息 (user_id 从 token 获取)
class MistakeNotebookEntryCreate(BaseModel):
    question_id: int
    # status 默认为 'new'，可以在添加时指定
    # notes 可以在添加时指定

# 更新时允许修改的字段
class MistakeNotebookEntryUpdate(BaseModel):
    status: Optional[str] = None # 允许更新状态
    notes: Optional[str] = None # 允许更新笔记
    last_reviewed_at: Optional[datetime] = None # 允许更新复习时间

# 数据库内部表示的基本模式
class MistakeNotebookEntryInDBBase(MistakeNotebookEntryBase):
    id: int
    user_id: int
    added_at: datetime

    class Config:
        from_attributes = True # Pydantic V2
        # orm_mode = True # Pydantic V1

# API 返回给客户端的模式 (包含嵌套的题目信息)
class MistakeNotebookEntryPublic(MistakeNotebookEntryInDBBase):
    # 嵌套完整的题目信息，方便前端显示
    question: Optional[PracticeQuestionWithOptions] = None

# (可选) 仅错题条目本身，不含题目详情
class MistakeNotebookEntry(MistakeNotebookEntryInDBBase):
    pass