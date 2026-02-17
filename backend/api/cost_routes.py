from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from typing import List, Optional
import structlog

from core.database import get_db
from models.cost_models import AzureCostData, NamespaceCostAllocation, KubernetesMetrics
from models.schemas import (
    CostOverviewResponse, NamespaceCostResponse, CostTrendResponse,
    NamespaceCostAllocation
)

logger = structlog.get_logger()
router = APIRouter(prefix="/costs", tags=["costs"])


@router.get("/overview", response_model=CostOverviewResponse)
async def get_cost_overview(
    period_start: Optional[datetime] = Query(None),
    period_end: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Get cost overview for the specified period
    """
    try:
        if not period_start:
            period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if not period_end:
            period_end = period_start + timedelta(days=32)
        
        # Get total Azure cost
        azure_query = select(func.sum(AzureCostData.cost)).where(
            and_(
                AzureCostData.date >= period_start,
                AzureCostData.date <= period_end
            )
        )
        azure_result = await db.execute(azure_query)
        total_azure_cost = azure_result.scalar() or 0.0
        
        # Get total Kubernetes allocated cost
        k8s_query = select(func.sum(NamespaceCostAllocation.total_cost)).where(
            and_(
                NamespaceCostAllocation.period_start >= period_start,
                NamespaceCostAllocation.period_end <= period_end
            )
        )
        k8s_result = await db.execute(k8s_query)
        total_k8s_cost = k8s_result.scalar() or 0.0
        
        # Get cost breakdown by service
        service_breakdown_query = select(
            AzureCostData.service_name,
            func.sum(AzureCostData.cost).label("total_cost")
        ).where(
            and_(
                AzureCostData.date >= period_start,
                AzureCostData.date <= period_end
            )
        ).group_by(AzureCostData.service_name)
        
        service_result = await db.execute(service_breakdown_query)
        cost_breakdown = {row.service_name: row.total_cost for row in service_result}
        
        return CostOverviewResponse(
            total_cost=total_azure_cost,
            azure_cost=total_azure_cost,
            kubernetes_cost=total_k8s_cost,
            period_start=period_start,
            period_end=period_end,
            cost_breakdown=cost_breakdown
        )
        
    except Exception as e:
        logger.error(f"Error getting cost overview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get cost overview")


@router.get("/namespaces", response_model=List[NamespaceCostResponse])
async def get_namespace_costs(
    period_start: Optional[datetime] = Query(None),
    period_end: Optional[datetime] = Query(None),
    cluster_name: Optional[str] = Query("default"),
    namespace: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Get cost breakdown by namespace
    """
    try:
        if not period_start:
            period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if not period_end:
            period_end = period_start + timedelta(days=32)
        
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
        
        namespace_costs = []
        for allocation in allocations:
            cost_breakdown = {
                "cpu": allocation.cpu_cost,
                "memory": allocation.memory_cost,
                "storage": allocation.storage_cost,
                "network": allocation.network_cost,
                "other": allocation.other_cost
            }
            
            namespace_costs.append(NamespaceCostResponse(
                namespace=allocation.namespace,
                cluster_name=allocation.cluster_name,
                total_cost=allocation.total_cost,
                cost_breakdown=cost_breakdown,
                period_start=allocation.period_start,
                period_end=allocation.period_end
            ))
        
        return namespace_costs
        
    except Exception as e:
        logger.error(f"Error getting namespace costs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get namespace costs")


@router.get("/trends", response_model=List[CostTrendResponse])
async def get_cost_trends(
    namespace: Optional[str] = Query(None),
    cluster_name: Optional[str] = Query("default"),
    months: int = Query(12, ge=1, le=24),
    db: AsyncSession = Depends(get_db)
):
    """
    Get cost trends over time
    """
    try:
        trends = []
        current_date = datetime.utcnow()
        
        for i in range(months):
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
            namespace_costs = {}
            for allocation in allocations:
                namespace_costs[allocation.namespace] = allocation.total_cost
            
            trends.append(CostTrendResponse(
                period=period_start.strftime("%Y-%m"),
                cost=total_cost,
                namespace_costs=namespace_costs
            ))
        
        return trends[::-1]  # Reverse to get chronological order
        
    except Exception as e:
        logger.error(f"Error getting cost trends: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get cost trends")


@router.get("/azure-resources")
async def get_azure_costs(
    period_start: Optional[datetime] = Query(None),
    period_end: Optional[datetime] = Query(None),
    resource_group: Optional[str] = Query(None),
    service_name: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Get Azure resource costs with filtering
    """
    try:
        if not period_start:
            period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if not period_end:
            period_end = period_start + timedelta(days=32)
        
        query = select(AzureCostData).where(
            and_(
                AzureCostData.date >= period_start,
                AzureCostData.date <= period_end
            )
        )
        
        if resource_group:
            query = query.where(AzureCostData.resource_group == resource_group)
        
        if service_name:
            query = query.where(AzureCostData.service_name == service_name)
        
        result = await db.execute(query)
        costs = result.scalars().all()
        
        return [
            {
                "id": cost.id,
                "subscription_id": cost.subscription_id,
                "resource_group": cost.resource_group,
                "resource_name": cost.resource_name,
                "resource_type": cost.resource_type,
                "service_name": cost.service_name,
                "cost": cost.cost,
                "currency": cost.currency,
                "date": cost.date,
                "tags": cost.tags
            }
            for cost in costs
        ]
        
    except Exception as e:
        logger.error(f"Error getting Azure costs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get Azure costs")


@router.get("/kubernetes-metrics")
async def get_kubernetes_metrics(
    namespace: Optional[str] = Query(None),
    cluster_name: Optional[str] = Query("default"),
    hours_back: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    """
    Get Kubernetes resource metrics
    """
    try:
        period_start = datetime.utcnow() - timedelta(hours=hours_back)
        period_end = datetime.utcnow()
        
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
        
        return [
            {
                "id": metric.id,
                "namespace": metric.namespace,
                "pod_name": metric.pod_name,
                "deployment_name": metric.deployment_name,
                "cpu_requests": metric.cpu_requests,
                "cpu_limits": metric.cpu_limits,
                "cpu_usage": metric.cpu_usage,
                "memory_requests": metric.memory_requests,
                "memory_limits": metric.memory_limits,
                "memory_usage": metric.memory_usage,
                "storage_requests": metric.storage_requests,
                "storage_usage": metric.storage_usage,
                "timestamp": metric.timestamp,
                "labels": metric.labels
            }
            for metric in metrics
        ]
        
    except Exception as e:
        logger.error(f"Error getting Kubernetes metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get Kubernetes metrics")
