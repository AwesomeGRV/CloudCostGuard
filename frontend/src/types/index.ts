export interface CostOverview {
  total_cost: number;
  azure_cost: number;
  kubernetes_cost: number;
  period_start: string;
  period_end: string;
  currency: string;
  cost_breakdown: Record<string, number>;
}

export interface NamespaceCost {
  namespace: string;
  cluster_name: string;
  total_cost: number;
  cost_breakdown: Record<string, number>;
  period_start: string;
  period_end: string;
}

export interface CostTrend {
  period: string;
  cost: number;
  namespace_costs: Record<string, number>;
}

export interface OptimizationRecommendation {
  id: number;
  namespace: string;
  cluster_name: string;
  resource_type: string;
  resource_name: string;
  recommendation_type: string;
  current_value: number;
  recommended_value: number;
  potential_savings: number;
  confidence_score: number;
  priority: 'high' | 'medium' | 'low';
  description: string;
  implementation_steps: string[];
  status: 'pending' | 'implemented' | 'dismissed';
  created_at: string;
  implemented_at?: string;
}

export interface CostComparison {
  id: number;
  namespace: string;
  cluster_name: string;
  current_period_cost: number;
  previous_period_cost: number;
  percentage_change: number;
  absolute_change: number;
  comparison_type: string;
  current_period_start: string;
  current_period_end: string;
  previous_period_start: string;
  previous_period_end: string;
  created_at: string;
}

export interface AzureCost {
  id: number;
  subscription_id: string;
  resource_group: string;
  resource_name: string;
  resource_type: string;
  service_name: string;
  cost: number;
  currency: string;
  date: string;
  tags: Record<string, any>;
}

export interface KubernetesMetric {
  id: number;
  namespace: string;
  pod_name: string;
  deployment_name: string;
  cpu_requests: number;
  cpu_limits: number;
  cpu_usage: number;
  memory_requests: number;
  memory_limits: number;
  memory_usage: number;
  storage_requests: number;
  storage_usage: number;
  timestamp: string;
  labels: Record<string, any>;
}

export interface EfficiencyMetrics {
  [namespace: string]: {
    avg_cpu_utilization: number;
    avg_memory_utilization: number;
    avg_storage_utilization: number;
    cpu_efficiency_score: 'good' | 'moderate' | 'poor';
    memory_efficiency_score: 'good' | 'moderate' | 'poor';
    storage_efficiency_score: 'good' | 'moderate' | 'poor';
    sample_count: number;
  };
}

export interface CostForecast {
  historical_data: CostTrend[];
  forecast: Array<{
    period: string;
    predicted_cost: number;
    confidence: 'high' | 'medium' | 'low';
  }>;
  trend_direction: 'increasing' | 'decreasing' | 'stable';
  monthly_change_rate: number;
  forecast_accuracy: string;
}

export interface TopSpender {
  namespace?: string;
  service_name?: string;
  total_cost: number;
  record_count: number;
  average_monthly_cost: number;
}

export interface TopSpendersResponse {
  period: {
    start: string;
    end: string;
    months: number;
  };
  top_namespaces: TopSpender[];
  top_services: TopSpender[];
}

export interface RecommendationsSummary {
  total_recommendations: number;
  pending_recommendations: number;
  implemented_recommendations: number;
  dismissed_recommendations: number;
  total_potential_savings: number;
  implemented_savings: number;
  priority_breakdown: {
    high: number;
    medium: number;
    low: number;
  };
  type_breakdown: Record<string, number>;
}
