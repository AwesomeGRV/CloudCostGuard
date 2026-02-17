import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from core.database import get_db
from models.cost_models import AzureCostData, KubernetesMetrics, NamespaceCostAllocation
from models.schemas import NamespaceCostAllocationCreate
import structlog

logger = structlog.get_logger()


class CostAnalyzer:
    def __init__(self):
        self.cpu_cost_per_core = 0.05  # $0.05 per core per hour
        self.memory_cost_per_gb = 0.01  # $0.01 per GB per hour
        self.storage_cost_per_gb = 0.0001  # $0.0001 per GB per hour
    
    async def calculate_namespace_costs(
        self, 
        period_start: datetime, 
        period_end: datetime,
        cluster_name: str = "default"
    ) -> List[NamespaceCostAllocation]:
        """
        Calculate cost allocation per namespace based on resource usage
        """
        try:
            # Get Kubernetes metrics for the period
            async for db in get_db():
                # Get total cluster cost from Azure data
                total_azure_cost = await self._get_total_azure_cost(db, period_start, period_end)
                
                # Get namespace resource usage
                namespace_usage = await self._get_namespace_resource_usage(
                    db, period_start, period_end, cluster_name
                )
                
                # Calculate cost allocation
                allocations = []
                total_cpu_usage = sum(ns['cpu_usage_hours'] for ns in namespace_usage.values())
                total_memory_usage = sum(ns['memory_usage_gb_hours'] for ns in namespace_usage.values())
                total_storage_usage = sum(ns['storage_usage_gb_hours'] for ns in namespace_usage.values())
                
                for namespace, usage in namespace_usage.items():
                    # Calculate cost components
                    cpu_cost = (usage['cpu_usage_hours'] / total_cpu_usage) * total_azure_cost if total_cpu_usage > 0 else 0
                    memory_cost = (usage['memory_usage_gb_hours'] / total_memory_usage) * total_azure_cost if total_memory_usage > 0 else 0
                    storage_cost = (usage['storage_usage_gb_hours'] / total_storage_usage) * total_azure_cost if total_storage_usage > 0 else 0
                    
                    # Alternative calculation using fixed rates
                    cpu_cost_fixed = usage['cpu_usage_hours'] * self.cpu_cost_per_core
                    memory_cost_fixed = usage['memory_usage_gb_hours'] * self.memory_cost_per_gb
                    storage_cost_fixed = usage['storage_usage_gb_hours'] * self.storage_cost_per_gb
                    
                    # Use proportional allocation of actual Azure costs
                    total_cost = cpu_cost + memory_cost + storage_cost
                    other_cost = max(0, total_azure_cost - sum(cpu_cost + memory_cost + storage_cost for ns in namespace_usage.values()))
                    
                    allocation = NamespaceCostAllocationCreate(
                        namespace=namespace,
                        cluster_name=cluster_name,
                        total_cost=total_cost,
                        cpu_cost=cpu_cost,
                        memory_cost=memory_cost,
                        storage_cost=storage_cost,
                        network_cost=0.0,  # Would need additional metrics
                        other_cost=other_cost,
                        period_start=period_start,
                        period_end=period_end,
                        allocation_method="resource_usage"
                    )
                    
                    allocations.append(NamespaceCostAllocation(**allocation.dict()))
                
                return allocations
                
        except Exception as e:
            logger.error(f"Error calculating namespace costs: {str(e)}")
            raise
    
    async def _get_total_azure_cost(
        self, 
        db: AsyncSession, 
        period_start: datetime, 
        period_end: datetime
    ) -> float:
        """
        Get total Azure cost for the period
        """
        try:
            query = select(func.sum(AzureCostData.cost)).where(
                and_(
                    AzureCostData.date >= period_start,
                    AzureCostData.date <= period_end
                )
            )
            result = await db.execute(query)
            total_cost = result.scalar() or 0.0
            return total_cost
            
        except Exception as e:
            logger.error(f"Error getting total Azure cost: {str(e)}")
            return 0.0
    
    async def _get_namespace_resource_usage(
        self,
        db: AsyncSession,
        period_start: datetime,
        period_end: datetime,
        cluster_name: str
    ) -> Dict[str, Dict[str, float]]:
        """
        Get aggregated resource usage by namespace
        """
        try:
            # Get metrics for the period
            query = select(KubernetesMetrics).where(
                and_(
                    KubernetesMetrics.timestamp >= period_start,
                    KubernetesMetrics.timestamp <= period_end,
                    KubernetesMetrics.cluster_name == cluster_name
                )
            )
            result = await db.execute(query)
            metrics = result.scalars().all()
            
            # Aggregate by namespace
            namespace_usage = {}
            hours_in_period = (period_end - period_start).total_seconds() / 3600
            
            for metric in metrics:
                namespace = metric.namespace
                if namespace not in namespace_usage:
                    namespace_usage[namespace] = {
                        'cpu_usage_hours': 0.0,
                        'memory_usage_gb_hours': 0.0,
                        'storage_usage_gb_hours': 0.0,
                        'sample_count': 0
                    }
                
                # Convert units and accumulate
                namespace_usage[namespace]['cpu_usage_hours'] += metric.cpu_usage * hours_in_period
                namespace_usage[namespace]['memory_usage_gb_hours'] += (metric.memory_usage / (1024**3)) * hours_in_period
                namespace_usage[namespace]['storage_usage_gb_hours'] += (metric.storage_usage / (1024**3)) * hours_in_period
                namespace_usage[namespace]['sample_count'] += 1
            
            # Average out the usage if we have multiple samples
            for namespace in namespace_usage:
                if namespace_usage[namespace]['sample_count'] > 1:
                    namespace_usage[namespace]['cpu_usage_hours'] /= namespace_usage[namespace]['sample_count']
                    namespace_usage[namespace]['memory_usage_gb_hours'] /= namespace_usage[namespace]['sample_count']
                    namespace_usage[namespace]['storage_usage_gb_hours'] /= namespace_usage[namespace]['sample_count']
            
            return namespace_usage
            
        except Exception as e:
            logger.error(f"Error getting namespace resource usage: {str(e)}")
            return {}
    
    async def store_cost_allocations(self, db: AsyncSession, allocations: List[NamespaceCostAllocation]):
        """
        Store cost allocations in the database
        """
        try:
            for allocation in allocations:
                db.add(allocation)
            
            await db.commit()
            logger.info(f"Stored {len(allocations)} cost allocation records")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error storing cost allocations: {str(e)}")
            raise
    
    async def run_analysis(
        self, 
        period_start: datetime = None, 
        period_end: datetime = None,
        cluster_name: str = "default"
    ):
        """
        Run the complete cost analysis
        """
        if not period_start:
            period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if not period_end:
            period_end = period_start + timedelta(days=30)
        
        logger.info(f"Starting cost analysis for period {period_start} to {period_end}")
        
        try:
            # Calculate namespace costs
            allocations = await self.calculate_namespace_costs(period_start, period_end, cluster_name)
            
            # Store allocations
            async for db in get_db():
                await self.store_cost_allocations(db, allocations)
            
            logger.info("Cost analysis completed successfully")
            return allocations
            
        except Exception as e:
            logger.error(f"Cost analysis failed: {str(e)}")
            raise


async def schedule_cost_analysis(cluster_name: str = "default"):
    """
    Scheduled task for cost analysis
    """
    analyzer = CostAnalyzer()
    await analyzer.run_analysis(cluster_name=cluster_name)
