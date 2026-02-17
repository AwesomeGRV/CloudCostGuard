import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from core.database import get_db
from models.cost_models import KubernetesMetrics, NamespaceCostAllocation, OptimizationRecommendation
from models.schemas import OptimizationRecommendationCreate, RecommendationTypeEnum, PriorityEnum
import structlog

logger = structlog.get_logger()


class RecommendationEngine:
    def __init__(self):
        self.cpu_utilization_threshold = 0.3  # 30% average utilization
        self.memory_utilization_threshold = 0.4  # 40% average utilization
        self.storage_utilization_threshold = 0.2  # 20% average utilization
        self.cost_savings_threshold = 10.0  # Minimum $10 savings to recommend
    
    async def generate_recommendations(
        self,
        cluster_name: str = "default",
        days_back: int = 7
    ) -> List[OptimizationRecommendation]:
        """
        Generate optimization recommendations based on usage patterns
        """
        try:
            recommendations = []
            period_start = datetime.utcnow() - timedelta(days=days_back)
            period_end = datetime.utcnow()
            
            async for db in get_db():
                # Get resource utilization data
                utilization_data = await self._get_resource_utilization(
                    db, period_start, period_end, cluster_name
                )
                
                # Get cost data for savings calculation
                cost_data = await self._get_namespace_costs(
                    db, period_start, period_end, cluster_name
                )
                
                # Generate recommendations for each resource
                for resource in utilization_data:
                    resource_recommendations = await self._analyze_resource(
                        resource, cost_data.get(resource['namespace'], 0)
                    )
                    recommendations.extend(resource_recommendations)
            
            logger.info(f"Generated {len(recommendations)} optimization recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise
    
    async def _get_resource_utilization(
        self,
        db: AsyncSession,
        period_start: datetime,
        period_end: datetime,
        cluster_name: str
    ) -> List[Dict[str, Any]]:
        """
        Get resource utilization data for analysis
        """
        try:
            query = select(KubernetesMetrics).where(
                and_(
                    KubernetesMetrics.timestamp >= period_start,
                    KubernetesMetrics.timestamp <= period_end,
                    KubernetesMetrics.cluster_name == cluster_name
                )
            )
            result = await db.execute(query)
            metrics = result.scalars().all()
            
            # Aggregate by namespace and deployment
            resource_data = {}
            for metric in metrics:
                key = f"{metric.namespace}:{metric.deployment_name}"
                if key not in resource_data:
                    resource_data[key] = {
                        'namespace': metric.namespace,
                        'deployment_name': metric.deployment_name,
                        'cpu_requests': [],
                        'cpu_limits': [],
                        'cpu_usage': [],
                        'memory_requests': [],
                        'memory_limits': [],
                        'memory_usage': [],
                        'storage_requests': [],
                        'storage_usage': []
                    }
                
                resource_data[key]['cpu_requests'].append(metric.cpu_requests)
                resource_data[key]['cpu_limits'].append(metric.cpu_limits)
                resource_data[key]['cpu_usage'].append(metric.cpu_usage)
                resource_data[key]['memory_requests'].append(metric.memory_requests)
                resource_data[key]['memory_limits'].append(metric.memory_limits)
                resource_data[key]['memory_usage'].append(metric.memory_usage)
                resource_data[key]['storage_requests'].append(metric.storage_requests)
                resource_data[key]['storage_usage'].append(metric.storage_usage)
            
            # Calculate averages
            utilization_list = []
            for key, data in resource_data.items():
                avg_cpu_utilization = (
                    sum(data['cpu_usage']) / sum(data['cpu_requests']) 
                    if sum(data['cpu_requests']) > 0 else 0
                )
                avg_memory_utilization = (
                    sum(data['memory_usage']) / sum(data['memory_requests']) 
                    if sum(data['memory_requests']) > 0 else 0
                )
                avg_storage_utilization = (
                    sum(data['storage_usage']) / sum(data['storage_requests']) 
                    if sum(data['storage_requests']) > 0 else 0
                )
                
                utilization_list.append({
                    'namespace': data['namespace'],
                    'deployment_name': data['deployment_name'],
                    'avg_cpu_utilization': avg_cpu_utilization,
                    'avg_memory_utilization': avg_memory_utilization,
                    'avg_storage_utilization': avg_storage_utilization,
                    'current_cpu_requests': sum(data['cpu_requests']) / len(data['cpu_requests']),
                    'current_memory_requests': sum(data['memory_requests']) / len(data['memory_requests']),
                    'current_storage_requests': sum(data['storage_requests']) / len(data['storage_requests'])
                })
            
            return utilization_list
            
        except Exception as e:
            logger.error(f"Error getting resource utilization: {str(e)}")
            return []
    
    async def _get_namespace_costs(
        self,
        db: AsyncSession,
        period_start: datetime,
        period_end: datetime,
        cluster_name: str
    ) -> Dict[str, float]:
        """
        Get costs by namespace for savings calculation
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
            
            return {allocation.namespace: allocation.total_cost for allocation in allocations}
            
        except Exception as e:
            logger.error(f"Error getting namespace costs: {str(e)}")
            return {}
    
    async def _analyze_resource(
        self,
        resource: Dict[str, Any],
        namespace_cost: float
    ) -> List[OptimizationRecommendationCreate]:
        """
        Analyze a single resource and generate recommendations
        """
        recommendations = []
        
        # CPU over-provisioning check
        if resource['avg_cpu_utilization'] < self.cpu_utilization_threshold:
            recommended_cpu = resource['current_cpu_requests'] * 0.5  # Recommend 50% reduction
            potential_savings = (resource['current_cpu_requests'] - recommended_cpu) * 0.05 * 24 * 30  # $0.05 per core per hour
            
            if potential_savings > self.cost_savings_threshold:
                recommendation = OptimizationRecommendationCreate(
                    namespace=resource['namespace'],
                    cluster_name="default",
                    resource_type="cpu",
                    resource_name=resource['deployment_name'],
                    recommendation_type=RecommendationTypeEnum.RIGHT_SIZE,
                    current_value=resource['current_cpu_requests'],
                    recommended_value=recommended_cpu,
                    potential_savings=potential_savings,
                    confidence_score=min(0.9, 1.0 - resource['avg_cpu_utilization']),
                    priority=PriorityEnum.HIGH if potential_savings > 50 else PriorityEnum.MEDIUM,
                    description=f"CPU utilization is only {resource['avg_cpu_utilization']:.1%}. Consider reducing CPU requests from {resource['current_cpu_requests']:.2f} to {recommended_cpu:.2f} cores.",
                    implementation_steps=[
                        f"Update deployment {resource['deployment_name']} CPU requests",
                        "Monitor performance after change",
                        "Adjust further if needed"
                    ]
                )
                recommendations.append(recommendation)
        
        # Memory over-provisioning check
        if resource['avg_memory_utilization'] < self.memory_utilization_threshold:
            recommended_memory = resource['current_memory_requests'] * 0.6  # Recommend 40% reduction
            potential_savings = ((resource['current_memory_requests'] - recommended_memory) / (1024**3)) * 0.01 * 24 * 30  # $0.01 per GB per hour
            
            if potential_savings > self.cost_savings_threshold:
                recommendation = OptimizationRecommendationCreate(
                    namespace=resource['namespace'],
                    cluster_name="default",
                    resource_type="memory",
                    resource_name=resource['deployment_name'],
                    recommendation_type=RecommendationTypeEnum.RIGHT_SIZE,
                    current_value=resource['current_memory_requests'],
                    recommended_value=recommended_memory,
                    potential_savings=potential_savings,
                    confidence_score=min(0.9, 1.0 - resource['avg_memory_utilization']),
                    priority=PriorityEnum.MEDIUM,
                    description=f"Memory utilization is only {resource['avg_memory_utilization']:.1%}. Consider reducing memory requests from {resource['current_memory_requests']/(1024**3):.2f}GB to {recommended_memory/(1024**3):.2f}GB.",
                    implementation_steps=[
                        f"Update deployment {resource['deployment_name']} memory requests",
                        "Monitor for OOM errors",
                        "Adjust further if needed"
                    ]
                )
                recommendations.append(recommendation)
        
        # Storage under-utilization check
        if resource['avg_storage_utilization'] < self.storage_utilization_threshold and resource['current_storage_requests'] > 0:
            recommended_storage = resource['current_storage_requests'] * 0.7  # Recommend 30% reduction
            potential_savings = ((resource['current_storage_requests'] - recommended_storage) / (1024**3)) * 0.0001 * 24 * 30  # $0.0001 per GB per hour
            
            if potential_savings > self.cost_savings_threshold:
                recommendation = OptimizationRecommendationCreate(
                    namespace=resource['namespace'],
                    cluster_name="default",
                    resource_type="storage",
                    resource_name=resource['deployment_name'],
                    recommendation_type=RecommendationTypeEnum.RIGHT_SIZE,
                    current_value=resource['current_storage_requests'],
                    recommended_value=recommended_storage,
                    potential_savings=potential_savings,
                    confidence_score=min(0.8, 1.0 - resource['avg_storage_utilization']),
                    priority=PriorityEnum.LOW,
                    description=f"Storage utilization is only {resource['avg_storage_utilization']:.1%}. Consider reducing PVC size.",
                    implementation_steps=[
                        f"Review PVC usage in namespace {resource['namespace']}",
                        "Resize PVCs if possible",
                        "Delete unused volumes"
                    ]
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    async def store_recommendations(self, db: AsyncSession, recommendations: List[OptimizationRecommendation]):
        """
        Store recommendations in the database
        """
        try:
            for recommendation in recommendations:
                db.add(recommendation)
            
            await db.commit()
            logger.info(f"Stored {len(recommendations)} optimization recommendations")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error storing recommendations: {str(e)}")
            raise
    
    async def run_recommendation_generation(
        self,
        cluster_name: str = "default",
        days_back: int = 7
    ):
        """
        Run the complete recommendation generation process
        """
        logger.info(f"Starting recommendation generation for cluster {cluster_name}")
        
        try:
            # Generate recommendations
            recommendations = await self.generate_recommendations(cluster_name, days_back)
            
            # Store recommendations
            async for db in get_db():
                await self.store_recommendations(db, recommendations)
            
            logger.info("Recommendation generation completed successfully")
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
            raise


async def schedule_recommendation_generation(cluster_name: str = "default"):
    """
    Scheduled task for recommendation generation
    """
    engine = RecommendationEngine()
    await engine.run_recommendation_generation(cluster_name)
