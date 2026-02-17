import React, { useState, useEffect } from 'react';
import { DollarSign, Server, Activity, TrendingUp } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import { costAPI, analyticsAPI } from '../services/api';
import { CostOverview, CostTrend, TopSpendersResponse } from '../types';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const Overview: React.FC = () => {
  const [costOverview, setCostOverview] = useState<CostOverview | null>(null);
  const [costTrends, setCostTrends] = useState<CostTrend[]>([]);
  const [topSpenders, setTopSpenders] = useState<TopSpendersResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [overview, trends, spenders] = await Promise.all([
          costAPI.getOverview(),
          costAPI.getCostTrends(undefined, 'default', 6),
          analyticsAPI.getTopSpenders('default', 3, 5)
        ]);

        setCostOverview(overview);
        setCostTrends(trends);
        setTopSpenders(spenders);
      } catch (error) {
        console.error('Error fetching overview data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">Loading overview...</div>
      </div>
    );
  }

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  const pieData = costOverview ? Object.entries(costOverview.cost_breakdown).map(([key, value]) => ({
    name: key,
    value: value
  })) : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Cost Overview</h1>
        <p className="text-gray-600">Monitor your cloud spending and resource utilization</p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Cost"
          value={costOverview?.total_cost || 0}
          format="currency"
          icon={<DollarSign className="w-6 h-6" />}
        />
        <MetricCard
          title="Azure Cost"
          value={costOverview?.azure_cost || 0}
          format="currency"
          icon={<Server className="w-6 h-6" />}
        />
        <MetricCard
          title="Kubernetes Cost"
          value={costOverview?.kubernetes_cost || 0}
          format="currency"
          icon={<Activity className="w-6 h-6" />}
        />
        <MetricCard
          title="Cost Trend"
          value={costTrends.length > 1 ? 
            ((costTrends[costTrends.length - 1].cost - costTrends[0].cost) / costTrends[0].cost * 100) : 0}
          format="percentage"
          change={costTrends.length > 1 ? 
            ((costTrends[costTrends.length - 1].cost - costTrends[0].cost) / costTrends[0].cost * 100) : undefined}
          icon={<TrendingUp className="w-6 h-6" />}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cost Trend Chart */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Cost Trend (6 Months)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={costTrends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" />
              <YAxis />
              <Tooltip formatter={(value) => [`$${Number(value).toFixed(2)}`, 'Cost']} />
              <Line 
                type="monotone" 
                dataKey="cost" 
                stroke="#3b82f6" 
                strokeWidth={2}
                dot={{ fill: '#3b82f6' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Cost Breakdown Pie Chart */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Cost Breakdown</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [`$${Number(value).toFixed(2)}`, 'Cost']} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Spenders */}
      {topSpenders && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Namespaces</h2>
            <div className="space-y-3">
              {topSpenders.top_namespaces.map((spender, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{spender.namespace}</p>
                    <p className="text-sm text-gray-600">{spender.record_count} records</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">${spender.total_cost.toFixed(2)}</p>
                    <p className="text-sm text-gray-600">${spender.average_monthly_cost.toFixed(2)}/mo</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Services</h2>
            <div className="space-y-3">
              {topSpenders.top_services.map((spender, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{spender.service_name}</p>
                    <p className="text-sm text-gray-600">{spender.record_count} records</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">${spender.total_cost.toFixed(2)}</p>
                    <p className="text-sm text-gray-600">${spender.average_monthly_cost.toFixed(2)}/mo</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Overview;
