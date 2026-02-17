import React, { useState, useEffect } from 'react';
import { Lightbulb, AlertTriangle, CheckCircle, Clock, DollarSign } from 'lucide-react';
import { recommendationsAPI } from '../services/api';
import { OptimizationRecommendation, RecommendationsSummary } from '../types';

const Recommendations: React.FC = () => {
  const [recommendations, setRecommendations] = useState<OptimizationRecommendation[]>([]);
  const [summary, setSummary] = useState<RecommendationsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({
    status: '',
    priority: '',
    namespace: ''
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [recs, summaryData] = await Promise.all([
          recommendationsAPI.getRecommendations(
            filter.namespace || undefined,
            'default',
            filter.status || undefined,
            filter.priority || undefined,
            50
          ),
          recommendationsAPI.getSummary(filter.namespace || undefined, 'default')
        ]);

        setRecommendations(recs);
        setSummary(summaryData);
      } catch (error) {
        console.error('Error fetching recommendations:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [filter]);

  const handleStatusUpdate = async (id: number, status: string) => {
    try {
      await recommendationsAPI.updateRecommendationStatus(id, status);
      // Refresh recommendations
      const recs = await recommendationsAPI.getRecommendations(
        filter.namespace || undefined,
        'default',
        filter.status || undefined,
        filter.priority || undefined,
        50
      );
      setRecommendations(recs);
    } catch (error) {
      console.error('Error updating recommendation status:', error);
    }
  };

  const generateRecommendations = async () => {
    try {
      await recommendationsAPI.generateRecommendations('default', 7);
      // Refresh data
      window.location.reload();
    } catch (error) {
      console.error('Error generating recommendations:', error);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-danger-600 bg-danger-100';
      case 'medium': return 'text-warning-600 bg-warning-100';
      case 'low': return 'text-success-600 bg-success-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return <Clock className="w-4 h-4" />;
      case 'implemented': return <CheckCircle className="w-4 h-4" />;
      case 'dismissed': return <AlertTriangle className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">Loading recommendations...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Optimization Recommendations</h1>
          <p className="text-gray-600">AI-powered cost optimization suggestions</p>
        </div>
        <button
          onClick={generateRecommendations}
          className="btn btn-primary flex items-center"
        >
          <Lightbulb className="w-4 h-4 mr-2" />
          Generate Recommendations
        </button>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="metric-card">
            <div className="flex items-center">
              <Lightbulb className="w-8 h-8 text-primary-600 mr-3" />
              <div>
                <p className="metric-label">Total Recommendations</p>
                <p className="metric-value">{summary.total_recommendations}</p>
              </div>
            </div>
          </div>
          
          <div className="metric-card">
            <div className="flex items-center">
              <Clock className="w-8 h-8 text-warning-600 mr-3" />
              <div>
                <p className="metric-label">Pending</p>
                <p className="metric-value">{summary.pending_recommendations}</p>
              </div>
            </div>
          </div>
          
          <div className="metric-card">
            <div className="flex items-center">
              <DollarSign className="w-8 h-8 text-success-600 mr-3" />
              <div>
                <p className="metric-label">Potential Savings</p>
                <p className="metric-value">${summary.total_potential_savings.toFixed(2)}</p>
              </div>
            </div>
          </div>
          
          <div className="metric-card">
            <div className="flex items-center">
              <CheckCircle className="w-8 h-8 text-primary-600 mr-3" />
              <div>
                <p className="metric-label">Implemented</p>
                <p className="metric-value">{summary.implemented_recommendations}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Filters</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={filter.status}
              onChange={(e) => setFilter({ ...filter, status: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All</option>
              <option value="pending">Pending</option>
              <option value="implemented">Implemented</option>
              <option value="dismissed">Dismissed</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
            <select
              value={filter.priority}
              onChange={(e) => setFilter({ ...filter, priority: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Namespace</label>
            <input
              type="text"
              value={filter.namespace}
              onChange={(e) => setFilter({ ...filter, namespace: e.target.value })}
              placeholder="Enter namespace..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
      </div>

      {/* Recommendations List */}
      <div className="space-y-4">
        {recommendations.map((rec) => (
          <div key={rec.id} className="card">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center mb-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium mr-2 ${getPriorityColor(rec.priority)}`}>
                    {rec.priority.toUpperCase()}
                  </span>
                  <span className="text-sm text-gray-500">
                    {rec.namespace} • {rec.resource_type}
                  </span>
                </div>
                
                <h3 className="text-lg font-medium text-gray-900 mb-2">{rec.description}</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                  <div>
                    <p className="text-sm text-gray-600">Current Value</p>
                    <p className="font-medium">{rec.current_value}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Recommended Value</p>
                    <p className="font-medium text-success-600">{rec.recommended_value}</p>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Potential Savings</p>
                    <p className="text-lg font-semibold text-success-600">
                      ${rec.potential_savings.toFixed(2)}
                    </p>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className="flex items-center text-sm text-gray-500">
                      {getStatusIcon(rec.status)}
                      <span className="ml-1">{rec.status}</span>
                    </span>
                    
                    {rec.status === 'pending' && (
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleStatusUpdate(rec.id, 'implemented')}
                          className="btn btn-success text-sm"
                        >
                          Implement
                        </button>
                        <button
                          onClick={() => handleStatusUpdate(rec.id, 'dismissed')}
                          className="btn btn-secondary text-sm"
                        >
                          Dismiss
                        </button>
                      </div>
                    )}
                  </div>
                </div>
                
                {rec.implementation_steps && rec.implementation_steps.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-sm font-medium text-gray-700 mb-2">Implementation Steps:</p>
                    <ol className="list-decimal list-inside text-sm text-gray-600 space-y-1">
                      {rec.implementation_steps.map((step, index) => (
                        <li key={index}>{step}</li>
                      ))}
                    </ol>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {recommendations.length === 0 && (
          <div className="text-center py-12">
            <Lightbulb className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No recommendations found</h3>
            <p className="text-gray-600">Try adjusting your filters or generate new recommendations.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Recommendations;
