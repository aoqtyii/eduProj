# app/api/endpoints/ai_analysis.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# 导入新的 service 和 schema
from app.services import ai_analysis_service
from app.schemas import ai_analysis as ai_schemas
from app import models, crud
from app.api import deps
from typing import List
from app.services import recommendation_service  # Import the new service
from app.schemas import recommendation as rec_schemas  # Import rec schemas

router = APIRouter()


@router.get("/student/dashboard", response_model=ai_schemas.StudentAIDashboardData)
async def read_student_ai_analysis(
        db: AsyncSession = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    获取当前登录学生的 AI 分析统计数据 Dashboard (增强版)。
    """
    try:
        # --- 修改点：调用更新后的 service 函数 ---
        analysis_data = await ai_analysis_service.get_student_ai_dashboard_data(db, user_id=current_user.id)
        return analysis_data
    except Exception as e:
        print(f"Error fetching AI dashboard data for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取 AI 分析数据时出错。"
        )


@router.get("/student/recommendations", response_model=List[rec_schemas.Recommendation])
async def get_student_recommendations(
        db: AsyncSession = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        limit: int = 5  # Limit the number of recommendations returned
):
    """
    获取当前学生的学习推荐（基于 AI 分析）。
    """
    # Option 1: Generate recommendations on-the-fly (can be slow)
    # await recommendation_service.generate_and_store_recommendations(db, user_id=current_user.id)

    # Option 2: Fetch pre-generated recommendations (preferred - generation done by background task or trigger)
    # For now, we'll generate on-the-fly for demonstration, but this should ideally be separate.
    try:
        await recommendation_service.generate_and_store_recommendations(db, user_id=current_user.id)
        recommendations = await crud.recommendation.get_multi_by_user(
            db, user_id=current_user.id, status='active', limit=limit
        )
        return recommendations
    except Exception as e:
        print(f"Error getting recommendations for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取学习推荐时出错。"
        )


@router.put("/student/recommendations/{recommendation_id}/dismiss", response_model=rec_schemas.Recommendation)
async def dismiss_recommendation(
        recommendation_id: int,
        db: AsyncSession = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    用户忽略一条推荐。
    """
    rec = await crud.recommendation.get(db, id=recommendation_id)
    if not rec or rec.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="推荐未找到或无权修改")
    if rec.status != 'active':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="推荐状态不是 active")
    updated_rec = await crud.recommendation.update_status(db=db, db_obj=rec, status='dismissed')
    return updated_rec

