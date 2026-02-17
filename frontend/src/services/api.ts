import axios from 'axios';
import {
  CostOverview,
  NamespaceCost,
  CostTrend,
  OptimizationRecommendation,
  CostComparison,
  AzureCost,
  KubernetesMetric,
  EfficiencyMetrics,
  CostForecast,
  TopSpendersResponse,
  RecommendationsSummary
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Request interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Cost API endpoints
export const costAPI = {
  getOverview: async (periodStart?: string, periodEnd?: string): Promise<CostOverview> => {
    const params = new URLSearchParams();
    if (periodStart) params.append('period_start', periodStart);
    if (periodEnd) params.append('period_end', periodEnd);
    
    const response = await api.get(`/costs/overview?${params}`);
    return response.data;
  },

  getNamespaceCosts: async (
    periodStart?: string,
    periodEnd?: string,
    clusterName?: string,
    namespace?: string
  ): Promise<NamespaceCost[]> => {
    const params = new URLSearchParams();
    if (periodStart) params.append('period_start', periodStart);
    if (periodEnd) params.append('period_end', periodEnd);
    if (clusterName) params.append('cluster_name', clusterName);
    if (namespace) params.append('namespace', namespace);
    
    const response = await api.get(`/costs/namespaces?${params}`);
    return response.data;
  },

  getCostTrends: async (
    namespace?: string,
    clusterName?: string,
    months?: number
  ): Promise<CostTrend[]> => {
    const params = new URLSearchParams();
    if (namespace) params.append('namespace', namespace);
    if (clusterName) params.append('cluster_name', clusterName);
    if (months) params.append('months', months.toString());
    
    const response = await api.get(`/costs/trends?${params}`);
    return response.data;
  },

  getAzureCosts: async (
    periodStart?: string,
    periodEnd?: string,
    resourceGroup?: string,
    serviceName?: string
  ): Promise<AzureCost[]> => {
    const params = new URLSearchParams();
    if (periodStart) params.append('period_start', periodStart);
    if (periodEnd) params.append('period_end', periodEnd);
    if (resourceGroup) params.append('resource_group', resourceGroup);
    if (serviceName) params.append('service_name', serviceName);
    
    const response = await api.get(`/costs/azure-resources?${params}`);
    return response.data;
  },

  getKubernetesMetrics: async (
    namespace?: string,
    clusterName?: string,
    hoursBack?: number
  ): Promise<KubernetesMetric[]> => {
    const params = new URLSearchParams();
    if (namespace) params.append('namespace', namespace);
    if (clusterName) params.append('cluster_name', clusterName);
    if (hoursBack) params.append('hours_back', hoursBack.toString());
    
    const response = await api.get(`/costs/kubernetes-metrics?${params}`);
    return response.data;
  },
};

// Recommendations API endpoints
export const recommendationsAPI = {
  getRecommendations: async (
    namespace?: string,
    clusterName?: string,
    status?: string,
    priority?: string,
    limit?: number
  ): Promise<OptimizationRecommendation[]> => {
    const params = new URLSearchParams();
    if (namespace) params.append('namespace', namespace);
    if (clusterName) params.append('cluster_name', clusterName);
    if (status) params.append('status', status);
    if (priority) params.append('priority', priority);
    if (limit) params.append('limit', limit.toString());
    
    const response = await api.get(`/recommendations/?${params}`);
    return response.data;
  },

  getRecommendation: async (id: number): Promise<OptimizationRecommendation> => {
    const response = await api.get(`/recommendations/${id}`);
    return response.data;
  },

  updateRecommendationStatus: async (id: number, status: string): Promise<void> => {
    await api.put(`/recommendations/${id}/status`, { status });
  },

  getSummary: async (
    namespace?: string,
    clusterName?: string
  ): Promise<RecommendationsSummary> => {
    const params = new URLSearchParams();
    if (namespace) params.append('namespace', namespace);
    if (clusterName) params.append('cluster_name', clusterName);
    
    const response = await api.get(`/recommendations/summary/overview?${params}`);
    return response.data;
  },

  generateRecommendations: async (
    clusterName?: string,
    daysBack?: number
  ): Promise<{ message: string; generated_count: number }> => {
    const params = new URLSearchParams();
    if (clusterName) params.append('cluster_name', clusterName || 'default');
    if (daysBack) params.append('days_back', daysBack.toString());
    
    const response = await api.post(`/recommendations/generate?${params}`);
    return response.data;
  },
};

// Analytics API endpoints
export const analyticsAPI = {
  getComparisons: async (
    comparisonType?: string,
    namespace?: string,
    clusterName?: string,
    limit?: number
  ): Promise<CostComparison[]> => {
    const params = new URLSearchParams();
    if (comparisonType) params.append('comparison_type', comparisonType);
    if (namespace) params.append('namespace', namespace);
    if (clusterName) params.append('cluster_name', clusterName);
    if (limit) params.append('limit', limit.toString());
    
    const response = await api.get(`/analytics/comparisons?${params}`);
    return response.data;
  },

  getEfficiencyMetrics: async (
    namespace?: string,
    clusterName?: string,
    daysBack?: number
  ): Promise<EfficiencyMetrics> => {
    const params = new URLSearchParams();
    if (namespace) params.append('namespace', namespace);
    if (clusterName) params.append('cluster_name', clusterName);
    if (daysBack) params.append('days_back', daysBack.toString());
    
    const response = await api.get(`/analytics/efficiency-metrics?${params}`);
    return response.data;
  },

  getCostForecast: async (
    namespace?: string,
    clusterName?: string,
    months?: number
  ): Promise<CostForecast> => {
    const params = new URLSearchParams();
    if (namespace) params.append('namespace', namespace);
    if (clusterName) params.append('cluster_name', clusterName);
    if (months) params.append('months', months.toString());
    
    const response = await api.get(`/analytics/cost-forecast?${params}`);
    return response.data;
  },

  getTopSpenders: async (
    clusterName?: string,
    periodMonths?: number,
    limit?: number
  ): Promise<TopSpendersResponse> => {
    const params = new URLSearchParams();
    if (clusterName) params.append('cluster_name', clusterName);
    if (periodMonths) params.append('period_months', periodMonths.toString());
    if (limit) params.append('limit', limit.toString());
    
    const response = await api.get(`/analytics/top-spenders?${params}`);
    return response.data;
  },
};

// Health check
export const healthAPI = {
  check: async (): Promise<{ status: string; timestamp: string; version: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};
