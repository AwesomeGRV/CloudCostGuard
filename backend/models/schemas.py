from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RecommendationTypeEnum(str, Enum):
    SCALE_DOWN = "scale_down"
    RIGHT_SIZE = "right_size"
    DELETE_UNUSED = "delete_unused"
    RESERVED_INSTANCES = "reserved_instances"
    SCHEDULED_SCALING = "scheduled_scaling"


class PriorityEnum(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class StatusEnum(str, Enum):
    PENDING = "pending"
    IMPLEMENTED = "implemented"
    DISMISSED = "dismissed"


class AzureCostDataBase(BaseModel):
    subscription_id: str
    resource_group: str
    resource_name: str
    resource_type: str
    service_name: str
    cost: float
    currency: str = "USD"
    date: datetime
    billing_period: str
    tags: Optional[Dict[str, Any]] = None


class AzureCostDataCreate(AzureCostDataBase):
    pass


class AzureCostData(AzureCostDataBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class KubernetesMetricsBase(BaseModel):
    namespace: str
    pod_name: str
    deployment_name: str
    cpu_requests: float
    cpu_limits: float
    cpu_usage: float
    memory_requests: float
    memory_limits: float
    memory_usage: float
    storage_requests: float
    storage_usage: float
    timestamp: datetime
    cluster_name: str
    labels: Optional[Dict[str, Any]] = None


class KubernetesMetricsCreate(KubernetesMetricsBase):
    pass


class KubernetesMetrics(KubernetesMetricsBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class NamespaceCostAllocationBase(BaseModel):
    namespace: str
    cluster_name: str
    total_cost: float
    cpu_cost: float
    memory_cost: float
    storage_cost: float
    network_cost: float
    other_cost: float
    period_start: datetime
    period_end: datetime
    allocation_method: str = "resource_usage"


class NamespaceCostAllocationCreate(NamespaceCostAllocationBase):
    pass


class NamespaceCostAllocation(NamespaceCostAllocationBase):
    id: int
    azure_cost_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class CostComparisonBase(BaseModel):
    namespace: str
    cluster_name: str
    current_period_cost: float
    previous_period_cost: float
    percentage_change: float
    absolute_change: float
    comparison_type: str
    current_period_start: datetime
    current_period_end: datetime
    previous_period_start: datetime
    previous_period_end: datetime


class CostComparisonCreate(CostComparisonBase):
    pass


class CostComparison(CostComparisonBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class OptimizationRecommendationBase(BaseModel):
    namespace: str
    cluster_name: str
    resource_type: str
    resource_name: str
    recommendation_type: RecommendationTypeEnum
    current_value: float
    recommended_value: float
    potential_savings: float
    confidence_score: float = Field(ge=0, le=1)
    priority: PriorityEnum
    description: str
    implementation_steps: List[str]
    status: StatusEnum = StatusEnum.PENDING


class OptimizationRecommendationCreate(OptimizationRecommendationBase):
    pass


class OptimizationRecommendation(OptimizationRecommendationBase):
    id: int
    created_at: datetime
    implemented_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CostOverviewResponse(BaseModel):
    total_cost: float
    azure_cost: float
    kubernetes_cost: float
    period_start: datetime
    period_end: datetime
    currency: str = "USD"
    cost_breakdown: Dict[str, float]


class NamespaceCostResponse(BaseModel):
    namespace: str
    cluster_name: str
    total_cost: float
    cost_breakdown: Dict[str, float]
    period_start: datetime
    period_end: datetime


class CostTrendResponse(BaseModel):
    period: str
    cost: float
    namespace_costs: Dict[str, float]
