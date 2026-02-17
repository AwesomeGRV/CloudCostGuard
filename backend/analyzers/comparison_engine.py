import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from core.database import get_db
from models.cost_models import NamespaceCostAllocation, CostComparison
from models.schemas import CostComparisonCreate
import structlog

logger = structlog.get_logger()


class ComparisonEngine:
    def __init__(self):
        pass
    
    async def compare_costs(
        self,
        comparison_type: str = "month-over-month",
        cluster_name: str = "default"
    ) -> List[CostComparison]:
        """
        Compare costs between current and previous periods
        """
        try:
            # Determine periods based on comparison type
            if comparison_type == "month-over-month":
                current_end = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                current_start = current_end - timedelta(days=32)
                current_start = current_start.replace(day=1)
                
                previous_end = current_start
                previous_start = previous_end - timedelta(days=32)
                previous_start = previous_start.replace(day=1)
            elif comparison_type == "week-over-week":
                current_end = datetime.utcnow()
                current_start = current_end - timedelta(days=7)
                
                previous_end = current_start
                previous_start = previous_end - timedelta(days=7)
            else:
                raise ValueError(f"Unsupported comparison type: {comparison_type}")
            
            # Get cost data for both periods
            async for db in get_db():
                current_costs = await self._get_period_costs(
                    db, current_start, current_end, cluster_name
                )
                previous_costs = await self._get_period_costs(
                    db, previous_start, previous_end, cluster_name
                )
                
                # Calculate comparisons
                comparisons = []
                all_namespaces = set(current_costs.keys()).union(set(previous_costs.keys()))
                
                for namespace in all_namespaces:
                    current_cost = current_costs.get(namespace, 0.0)
                    previous_cost = previous_costs.get(namespace, 0.0)
                    
                    if previous_cost == 0:
                        percentage_change = float('inf') if current_cost > 0 else 0.0
                    else:
                        percentage_change = ((current_cost - previous_cost) / previous_cost) * 100
                    
                    absolute_change = current_cost - previous_cost
                    
                    comparison = CostComparisonCreate(
                        namespace=namespace,
                        cluster_name=cluster_name,
                        current_period_cost=current_cost,
                        previous_period_cost=previous_cost,
                        percentage_change=percentage_change,
                        absolute_change=absolute_change,
                        comparison_type=comparison_type,
                        current_period_start=current_start,
                        current_period_end=current_end,
                        previous_period_start=previous_start,
                        previous_period_end=previous_end
                    )
                    
                    comparisons.append(CostComparison(**comparison.dict()))
                
                return comparisons
                
        except Exception as e:
            logger.error(f"Error comparing costs: {str(e)}")
            raise
    
    async def _get_period_costs(
        self,
        db: AsyncSession,
        period_start: datetime,
        period_end: datetime,
        cluster_name: str
    ) -> Dict[str, float]:
        """
        Get total costs by namespace for a specific period
        """
        try:
            query = select(NamespaceCostAllocation).where(
                and_(
                    NamespaceCostAllocation.period_start >= period_start,
                    NamespaceCostAllocation.period_end <= period_end,
                    NamespaceCostAllocation.cluster_name == cluster_name
                )
            )
            result = await db.execute(query)
            allocations = result.scalars().all()
            
            # Aggregate by namespace
            namespace_costs = {}
            for allocation in allocations:
                if allocation.namespace not in namespace_costs:
                    namespace_costs[allocation.namespace] = 0.0
                namespace_costs[allocation.namespace] += allocation.total_cost
            
            return namespace_costs
            
        except Exception as e:
            logger.error(f"Error getting period costs: {str(e)}")
            return {}
    
    async def store_comparisons(self, db: AsyncSession, comparisons: List[CostComparison]):
        """
        Store cost comparisons in the database
        """
        try:
            for comparison in comparisons:
                db.add(comparison)
            
            await db.commit()
            logger.info(f"Stored {len(comparisons)} cost comparison records")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error storing cost comparisons: {str(e)}")
            raise
    
    async def get_cost_trends(
        self,
        namespace: str = None,
        cluster_name: str = "default",
        months: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Get cost trends over time
        """
        try:
            async for db in get_db():
                # Get monthly cost data
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
                    
                    trends.append({
                        "period": period_start.strftime("%Y-%m"),
                        "cost": total_cost,
                        "namespace_costs": namespace_costs
                    })
                
                return trends[::-1]  # Reverse to get chronological order
                
        except Exception as e:
            logger.error(f"Error getting cost trends: {str(e)}")
            return []
    
    async def run_comparison(
        self,
        comparison_type: str = "month-over-month",
        cluster_name: str = "default"
    ):
        """
        Run the complete cost comparison
        """
        logger.info(f"Starting cost comparison: {comparison_type}")
        
        try:
            # Compare costs
            comparisons = await self.compare_costs(comparison_type, cluster_name)
            
            # Store comparisons
            async for db in get_db():
                await self.store_comparisons(db, comparisons)
            
            logger.info("Cost comparison completed successfully")
            return comparisons
            
        except Exception as e:
            logger.error(f"Cost comparison failed: {str(e)}")
            raise


async def schedule_cost_comparison(comparison_type: str = "month-over-month", cluster_name: str = "default"):
    """
    Scheduled task for cost comparison
    """
    engine = ComparisonEngine()
    await engine.run_comparison(comparison_type, cluster_name)
