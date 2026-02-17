from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class AzureCostData(Base):
    __tablename__ = "azure_cost_data"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(String, index=True)
    resource_group = Column(String, index=True)
    resource_name = Column(String)
    resource_type = Column(String)
    service_name = Column(String)
    cost = Column(Float)
    currency = Column(String, default="USD")
    date = Column(DateTime, index=True)
    billing_period = Column(String)
    tags = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    namespace_allocation = relationship("NamespaceCostAllocation", back_populates="azure_cost")


class KubernetesMetrics(Base):
    __tablename__ = "kubernetes_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    namespace = Column(String, index=True)
    pod_name = Column(String)
    deployment_name = Column(String)
    cpu_requests = Column(Float)
    cpu_limits = Column(Float)
    cpu_usage = Column(Float)
    memory_requests = Column(Float)
    memory_limits = Column(Float)
    memory_usage = Column(Float)
    storage_requests = Column(Float)
    storage_usage = Column(Float)
    timestamp = Column(DateTime, index=True)
    cluster_name = Column(String)
    labels = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class NamespaceCostAllocation(Base):
    __tablename__ = "namespace_cost_allocation"
    
    id = Column(Integer, primary_key=True, index=True)
    namespace = Column(String, index=True)
    cluster_name = Column(String)
    total_cost = Column(Float)
    cpu_cost = Column(Float)
    memory_cost = Column(Float)
    storage_cost = Column(Float)
    network_cost = Column(Float)
    other_cost = Column(Float)
    period_start = Column(DateTime, index=True)
    period_end = Column(DateTime, index=True)
    allocation_method = Column(String, default="resource_usage")
    azure_cost_id = Column(Integer, ForeignKey("azure_cost_data.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    azure_cost = relationship("AzureCostData", back_populates="namespace_allocation")


class CostComparison(Base):
    __tablename__ = "cost_comparison"
    
    id = Column(Integer, primary_key=True, index=True)
    namespace = Column(String, index=True)
    cluster_name = Column(String)
    current_period_cost = Column(Float)
    previous_period_cost = Column(Float)
    percentage_change = Column(Float)
    absolute_change = Column(Float)
    comparison_type = Column(String)  # month-over-month, week-over-week
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    previous_period_start = Column(DateTime)
    previous_period_end = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class OptimizationRecommendation(Base):
    __tablename__ = "optimization_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    namespace = Column(String, index=True)
    cluster_name = Column(String)
    resource_type = Column(String)  # cpu, memory, storage, etc.
    resource_name = Column(String)
    recommendation_type = Column(String)  # scale_down, right_size, delete_unused
    current_value = Column(Float)
    recommended_value = Column(Float)
    potential_savings = Column(Float)
    confidence_score = Column(Float)  # 0-1
    priority = Column(String)  # high, medium, low
    description = Column(Text)
    implementation_steps = Column(JSON)
    status = Column(String, default="pending")  # pending, implemented, dismissed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    implemented_at = Column(DateTime(timezone=True), nullable=True)
