# app/services/recommendation_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from typing import List, Dict
import random  # For placeholder logic

from app import crud, models, schemas
from app.schemas import recommendation as rec_schemas


# --- Placeholder AI Logic ---
async def analyze_mistakes_and_generate_recommendations(
        db: AsyncSession, user_id: int
) -> List[rec_schemas.RecommendationCreate]:
    """
    Analyzes user mistakes and generates practice recommendations.
    THIS IS A PLACEHOLDER - Replace with actual AI/ML logic.
    """
    recommendations_to_create: List[rec_schemas.RecommendationCreate] = []

    # 1. Get user's recent mistakes ('new' or 'reviewed' status) with knowledge points
    stmt = (
        select(models.MistakeNotebookEntry)
        .options(
            joinedload(models.MistakeNotebookEntry.question)
            .joinedload(models.PracticeQuestion.knowledge_point_associations)
            .joinedload(models.QuestionKnowledgePoint.knowledge_point)  # Load KP details
        )
        .filter(
            models.MistakeNotebookEntry.user_id == user_id,
            models.MistakeNotebookEntry.status.in_(['new', 'reviewed'])
        )
        .order_by(models.MistakeNotebookEntry.added_at.desc())
        .limit(20)  # Analyze recent 20 mistakes
    )
    result = await db.execute(stmt)
    mistakes = result.scalars().unique().all()

    if not mistakes:
        return []  # No mistakes to analyze

    # 2. Aggregate mistakes by knowledge point (PLACEHOLDER LOGIC)
    kp_mistake_counts: Dict[int, Dict] = {}
    for mistake in mistakes:
        if mistake.question:
            for assoc in mistake.question.knowledge_point_associations:
                kp = assoc.knowledge_point
                if kp:
                    if kp.id not in kp_mistake_counts:
                        kp_mistake_counts[kp.id] = {"count": 0, "name": kp.name, "id": kp.id}
                    kp_mistake_counts[kp.id]["count"] += 1

    # 3. Identify "weak" knowledge points (PLACEHOLDER: simply points with > 1 mistake)
    weak_kps = [kp_info for kp_info in kp_mistake_counts.values() if kp_info["count"] > 1]
    weak_kps.sort(key=lambda x: x["count"], reverse=True)  # Sort by most frequent mistakes

    # 4. Find related practice modules (PLACEHOLDER: find modules containing questions with weak KPs)
    generated_module_recs = set()
    if weak_kps:
        # Get IDs of top 2 weak KPs
        top_weak_kp_ids = [kp["id"] for kp in weak_kps[:2]]

        # Find modules that have questions linked to these weak KPs
        module_stmt = (
            select(models.PracticeModule)
            .options(joinedload(models.PracticeModule.questions))  # Load questions briefly
            .join(models.PracticeQuestion, models.PracticeModule.id == models.PracticeQuestion.module_id)
            .join(models.QuestionKnowledgePoint,
                  models.PracticeQuestion.id == models.QuestionKnowledgePoint.question_id)
            .filter(models.QuestionKnowledgePoint.knowledge_point_id.in_(top_weak_kp_ids))
            .distinct()  # Ensure modules aren't duplicated
            .limit(3)  # Limit to 3 module recommendations
        )
        module_result = await db.execute(module_stmt)
        related_modules = module_result.scalars().all()

        for module in related_modules:
            if module.id not in generated_module_recs:
                recommendations_to_create.append(rec_schemas.RecommendationCreate(
                    user_id=user_id,
                    recommendation_type='practice_module',
                    related_item_id=module.id,
                    related_item_name=f"练习模块: {module.title}",
                    reason=f"检测到在与此模块相关的知识点 ({', '.join([kp['name'] for kp in weak_kps if kp['id'] in top_weak_kp_ids])}) 上存在较多错题。",
                    priority=1  # Medium priority
                ))
                generated_module_recs.add(module.id)

    # 5. (Optional Placeholder) Add a general recommendation if few specific ones found
    if not recommendations_to_create and mistakes:
        recommendations_to_create.append(rec_schemas.RecommendationCreate(
            user_id=user_id,
            recommendation_type='general_review',
            reason="建议您回顾一下最近的错题。",
            priority=0  # Low priority
        ))

    return recommendations_to_create


async def generate_and_store_recommendations(db: AsyncSession, user_id: int):
    """
    Generates recommendations and stores them, potentially clearing old ones.
    """
    # 1. (Optional) Clear old/active recommendations for the user
    # await db.execute(delete(models.Recommendation).where(Recommendation.user_id == user_id, Recommendation.status == 'active'))

    # 2. Generate new recommendations using the (placeholder) AI logic
    new_recs_data = await analyze_mistakes_and_generate_recommendations(db, user_id)

    # 3. Store the new recommendations
    for rec_data in new_recs_data:
        await crud.recommendation.create_recommendation(db=db, obj_in=rec_data)

    await db.flush()  # Ensure changes are persisted before subsequent reads in the same request cycle if needed
