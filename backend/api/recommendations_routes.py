from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from datetime import datetime
from typing import List, Optional
import structlog

from core.database import get_db
from models.cost_models import OptimizationRecommendation
from models.schemas import OptimizationRecommendation, StatusEnum, PriorityEnum

logger = structlog.get_logger()
router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/", response_model=List[OptimizationRecommendation])
async def get_recommendations(
    namespace: Optional[str] = Query(None),
    cluster_name: Optional[str] = Query("default"),
    status: Optional[StatusEnum] = Query(None),
    priority: Optional[PriorityEnum] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get optimization recommendations with filtering
    """
    try:
        query = select(OptimizationRecommendation).where(
            OptimizationRecommendation.cluster_name == cluster_name
        )
        
        if namespace:
            query = query.where(OptimizationRecommendation.namespace == namespace)
        
        if status:
            query = query.where(OptimizationRecommendation.status == status)
        
        if priority:
            query = query.where(OptimizationRecommendation.priority == priority)
        
        query = query.order_by(
            OptimizationRecommendation.priority.desc(),
            OptimizationRecommendation.potential_savings.desc()
        ).limit(limit)
        
        result = await db.execute(query)
        recommendations = result.scalars().all()
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")


@router.get("/{recommendation_id}", response_model=OptimizationRecommendation)
async def get_recommendation(
    recommendation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific recommendation by ID
    """
    try:
        query = select(OptimizationRecommendation).where(
            OptimizationRecommendation.id == recommendation_id
        )
        result = await db.execute(query)
        recommendation = result.scalar_one_or_none()
        
        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        return recommendation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendation {recommendation_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get recommendation")


@router.put("/{recommendation_id}/status")
async def update_recommendation_status(
    recommendation_id: int,
    status: StatusEnum,
    db: AsyncSession = Depends(get_db)
):
    """
    Update recommendation status
    """
    try:
        # Check if recommendation exists
        get_query = select(OptimizationRecommendation).where(
            OptimizationRecommendation.id == recommendation_id
        )
        result = await db.execute(get_query)
        recommendation = result.scalar_one_or_none()
        
        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        # Update status
        update_data = {"status": status}
        if status == StatusEnum.IMPLEMENTED:
            update_data["implemented_at"] = datetime.utcnow()
        
        update_query = update(OptimizationRecommendation).where(
            OptimizationRecommendation.id == recommendation_id
        ).values(**update_data)
        
        await db.execute(update_query)
        await db.commit()
        
        return {"message": f"Recommendation status updated to {status}"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating recommendation status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update recommendation status")


@router.get("/summary/overview")
async def get_recommendations_summary(
    namespace: Optional[str] = Query(None),
    cluster_name: Optional[str] = Query("default"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recommendations summary overview
    """
    try:
        base_query = select(OptimizationRecommendation).where(
            OptimizationRecommendation.cluster_name == cluster_name
        )
        
        if namespace:
            base_query = base_query.where(OptimizationRecommendation.namespace == namespace)
        
        # Get all recommendations
        result = await db.execute(base_query)
        all_recommendations = result.scalars().all()
        
        # Calculate summary statistics
        total_recommendations = len(all_recommendations)
        pending_recommendations = len([r for r in all_recommendations if r.status == StatusEnum.PENDING])
        implemented_recommendations = len([r for r in all_recommendations if r.status == StatusEnum.IMPLEMENTED])
        dismissed_recommendations = len([r for r in all_recommendations if r.status == StatusEnum.DISMISSED])
        
        # Calculate potential savings
        total_potential_savings = sum(r.potential_savings for r in all_recommendations if r.status == StatusEnum.PENDING)
        implemented_savings = sum(r.potential_savings for r in all_recommendations if r.status == StatusEnum.IMPLEMENTED)
        
        # Group by priority
        high_priority = len([r for r in all_recommendations if r.priority == PriorityEnum.HIGH and r.status == StatusEnum.PENDING])
        medium_priority = len([r for r in all_recommendations if r.priority == PriorityEnum.MEDIUM and r.status == StatusEnum.PENDING])
        low_priority = len([r for r in all_recommendations if r.priority == PriorityEnum.LOW and r.status == StatusEnum.PENDING])
        
        # Group by recommendation type
        type_counts = {}
        for rec in all_recommendations:
            if rec.recommendation_type not in type_counts:
                type_counts[rec.recommendation_type] = 0
            type_counts[rec.recommendation_type] += 1
        
        return {
            "total_recommendations": total_recommendations,
            "pending_recommendations": pending_recommendations,
            "implemented_recommendations": implemented_recommendations,
            "dismissed_recommendations": dismissed_recommendations,
            "total_potential_savings": total_potential_savings,
            "implemented_savings": implemented_savings,
            "priority_breakdown": {
                "high": high_priority,
                "medium": medium_priority,
                "low": low_priority
            },
            "type_breakdown": type_counts
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendations summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations summary")


@router.post("/generate")
async def trigger_recommendation_generation(
    cluster_name: str = Query("default"),
    days_back: int = Query(7, ge=1, le=30)
):
    """
    Trigger manual recommendation generation
    """
    try:
        from recommendations.recommendation_engine import schedule_recommendation_generation
        import asyncio
        
        # Run recommendation generation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        recommendations = loop.run_until_complete(
            schedule_recommendation_generation(cluster_name)
        )
        
        return {
            "message": "Recommendation generation completed",
            "generated_count": len(recommendations)
        }
        
    except Exception as e:
        logger.error(f"Error triggering recommendation generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")
