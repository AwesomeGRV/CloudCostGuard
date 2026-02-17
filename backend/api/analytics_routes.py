from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import structlog

from core.database import get_db
from models.cost_models import CostComparison, NamespaceCostAllocation, OptimizationRecommendation
from models.schemas import CostComparison

logger = structlog.get_logger()
router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/comparisons", response_model=List[CostComparison])
async def get_cost_comparisons(
    comparison_type: Optional[str] = Query("month-over-month"),
    namespace: Optional[str] = Query(None),
    cluster_name: Optional[str] = Query("default"),
    limit: int = Query(12, ge=1, le=24),
    db: AsyncSession = Depends(get_db)
):
    """
    Get cost comparisons between periods
    """
    try:
        query = select(CostComparison).where(
            and_(
                CostComparison.comparison_type == comparison_type,
                CostComparison.cluster_name == cluster_name
            )
        )
        
        if namespace:
            query = query.where(CostComparison.namespace == namespace)
        
        query = query.order_by(CostComparison.current_period_start.desc()).limit(limit)
        
        result = await db.execute(query)
        comparisons = result.scalars().all()
        
        return comparisons
        
    except Exception as e:
        logger.error(f"Error getting cost comparisons: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get cost comparisons")


@router.get("/efficiency-metrics")
async def get_efficiency_metrics(
    namespace: Optional[str] = Query(None),
    cluster_name: Optional[str] = Query("default"),
    days_back: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """
    Get resource efficiency metrics
    """
    try:
        from models.cost_models import KubernetesMetrics
        
        period_start = datetime.utcnow() - timedelta(days=days_back)
        period_end = datetime.utcnow()
        
        # Get Kubernetes metrics for the period
        query = select(KubernetesMetrics).where(
            and_(
                KubernetesMetrics.timestamp >= period_start,
                KubernetesMetrics.timestamp <= period_end,
                KubernetesMetrics.cluster_name == cluster_name
            )
        )
        
        if namespace:
            query = query.where(KubernetesMetrics.namespace == namespace)
        
        result = await db.execute(query)
        metrics = result.scalars().all()
        
        if not metrics:
            return {"message": "No metrics data available for the specified period"}
        
        # Calculate efficiency metrics
        efficiency_data = {}
        
        for metric in metrics:
            ns = metric.namespace
            if ns not in efficiency_data:
                efficiency_data[ns] = {
                    "cpu_utilization_samples": [],
                    "memory_utilization_samples": [],
                    "storage_utilization_samples": []
                }
            
            # Calculate utilization ratios
            cpu_utilization = (
                metric.cpu_usage / metric.cpu_requests 
                if metric.cpu_requests > 0 else 0
            )
            memory_utilization = (
                metric.memory_usage / metric.memory_requests 
                if metric.memory_requests > 0 else 0
            )
            storage_utilization = (
                metric.storage_usage / metric.storage_requests 
                if metric.storage_requests > 0 else 0
            )
            
            efficiency_data[ns]["cpu_utilization_samples"].append(cpu_utilization)
            efficiency_data[ns]["memory_utilization_samples"].append(memory_utilization)
            efficiency_data[ns]["storage_utilization_samples"].append(storage_utilization)
        
        # Calculate averages and identify inefficiencies
        results = {}
        for ns, data in efficiency_data.items():
            avg_cpu_utilization = sum(data["cpu_utilization_samples"]) / len(data["cpu_utilization_samples"])
            avg_memory_utilization = sum(data["memory_utilization_samples"]) / len(data["memory_utilization_samples"])
            avg_storage_utilization = sum(data["storage_utilization_samples"]) / len(data["storage_utilization_samples"])
            
            results[ns] = {
                "avg_cpu_utilization": round(avg_cpu_utilization, 3),
                "avg_memory_utilization": round(avg_memory_utilization, 3),
                "avg_storage_utilization": round(avg_storage_utilization, 3),
                "cpu_efficiency_score": "good" if avg_cpu_utilization > 0.3 else "poor" if avg_cpu_utilization < 0.1 else "moderate",
                "memory_efficiency_score": "good" if avg_memory_utilization > 0.4 else "poor" if avg_memory_utilization < 0.1 else "moderate",
                "storage_efficiency_score": "good" if avg_storage_utilization > 0.2 else "poor" if avg_storage_utilization < 0.05 else "moderate",
                "sample_count": len(data["cpu_utilization_samples"])
            }
        
        return results
        
    except Exception as e:
        logger.error(f"Error getting efficiency metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get efficiency metrics")


@router.get("/cost-forecast")
async def get_cost_forecast(
    namespace: Optional[str] = Query(None),
    cluster_name: Optional[str] = Query("default"),
    months: int = Query(3, ge=1, le=6),
    db: AsyncSession = Depends(get_db)
):
    """
    Get cost forecast based on historical trends
    """
    try:
        # Get historical cost data
        trends = []
        current_date = datetime.utcnow()
        
        for i in range(months * 2):  # Get double the months for better prediction
            period_end = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            period_end = period_end - timedelta(days=i * 30)
            period_start = period_end - timedelta(days=30)
            
            query = select(NamespaceCostAllocation).where(
                and_(
                    NamespaceCostAllocation.period_start >= period_start,
                    NamespaceCostAllocation.period_end <= period_end,
                    NamespaceCostAllocation.cluster_name == cluster_name
                )
            )
            
            if namespace:
                query = query.where(NamespaceCostAllocation.namespace == namespace)
            
            result = await db.execute(query)
            allocations = result.scalars().all()
            
            total_cost = sum(allocation.total_cost for allocation in allocations)
            trends.append({
                "period": period_start.strftime("%Y-%m"),
                "cost": total_cost
            })
        
        trends = trends[::-1]  # Reverse to get chronological order
        
        if len(trends) < 2:
            return {"message": "Insufficient historical data for forecasting"}
        
        # Simple linear regression for forecasting
        def linear_regression(x_values, y_values):
            n = len(x_values)
            sum_x = sum(x_values)
            sum_y = sum(y_values)
            sum_xy = sum(x * y for x, y in zip(x_values, y_values))
            sum_x2 = sum(x * x for x in x_values)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            
            return slope, intercept
        
        # Prepare data for regression
        x_values = list(range(len(trends)))
        y_values = [trend["cost"] for trend in trends]
        
        slope, intercept = linear_regression(x_values, y_values)
        
        # Generate forecast
        forecast = []
        for i in range(1, months + 1):
            future_x = len(trends) + i - 1
            predicted_cost = slope * future_x + intercept
            
            # Calculate forecast period
            forecast_date = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            forecast_date = forecast_date + timedelta(days=i * 30)
            
            forecast.append({
                "period": forecast_date.strftime("%Y-%m"),
                "predicted_cost": max(0, predicted_cost),  # Ensure non-negative
                "confidence": "low" if i > 3 else "medium" if i > 1 else "high"
            })
        
        # Calculate trend direction
        trend_direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
        
        return {
            "historical_data": trends,
            "forecast": forecast,
            "trend_direction": trend_direction,
            "monthly_change_rate": slope,
            "forecast_accuracy": "moderate"  # Could be improved with more sophisticated models
        }
        
    except Exception as e:
        logger.error(f"Error getting cost forecast: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get cost forecast")


@router.get("/top-spenders")
async def get_top_spenders(
    cluster_name: Optional[str] = Query("default"),
    period_months: int = Query(1, ge=1, le=12),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Get top spending namespaces or resources
    """
    try:
        period_start = datetime.utcnow() - timedelta(days=period_months * 30)
        period_end = datetime.utcnow()
        
        # Get top spending namespaces
        namespace_query = select(
            NamespaceCostAllocation.namespace,
            func.sum(NamespaceCostAllocation.total_cost).label("total_cost"),
            func.count(NamespaceCostAllocation.id).label("record_count")
        ).where(
            and_(
                NamespaceCostAllocation.period_start >= period_start,
                NamespaceCostAllocation.period_end <= period_end,
                NamespaceCostAllocation.cluster_name == cluster_name
            )
        ).group_by(NamespaceCostAllocation.namespace).order_by(
            func.sum(NamespaceCostAllocation.total_cost).desc()
        ).limit(limit)
        
        namespace_result = await db.execute(namespace_query)
        top_namespaces = namespace_result.all()
        
        # Get top spending Azure services
        from models.cost_models import AzureCostData
        
        service_query = select(
            AzureCostData.service_name,
            func.sum(AzureCostData.cost).label("total_cost"),
            func.count(AzureCostData.id).label("record_count")
        ).where(
            and_(
                AzureCostData.date >= period_start,
                AzureCostData.date <= period_end
            )
        ).group_by(AzureCostData.service_name).order_by(
            func.sum(AzureCostData.cost).desc()
        ).limit(limit)
        
        service_result = await db.execute(service_query)
        top_services = service_result.all()
        
        return {
            "period": {
                "start": period_start,
                "end": period_end,
                "months": period_months
            },
            "top_namespaces": [
                {
                    "namespace": ns.namespace,
                    "total_cost": ns.total_cost,
                    "record_count": ns.record_count,
                    "average_monthly_cost": ns.total_cost / period_months
                }
                for ns in top_namespaces
            ],
            "top_services": [
                {
                    "service_name": service.service_name,
                    "total_cost": service.total_cost,
                    "record_count": service.record_count,
                    "average_monthly_cost": service.total_cost / period_months
                }
                for service in top_services
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting top spenders: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get top spenders")
