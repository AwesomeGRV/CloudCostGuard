import React from 'react';
import AzureCostForm from './AzureCostForm';

function App() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>CloudCostGuard Demo</h1>
      <p>Welcome to the CloudCostGuard FinOps Platform!</p>
      
      <div style={{ marginTop: '20px' }}>
        <h2>🚀 Application Status</h2>
        <p>✅ Backend Server: Running on http://localhost:8000</p>
        <p>✅ Frontend Server: Running on http://localhost:3000</p>
        <p>✅ API Health: Healthy</p>
      </div>

      <AzureCostForm />
      
      <div style={{ marginTop: '40px' }}>
        <h2>📊 Available API Endpoints</h2>
        <ul>
          <li><a href="http://localhost:8000/health" target="_blank" rel="noopener noreferrer">Health Check</a></li>
          <li><a href="http://localhost:8000/api/v1/costs/overview" target="_blank" rel="noopener noreferrer">Cost Overview</a></li>
          <li><a href="http://localhost:8000/api/v1/costs/namespaces" target="_blank" rel="noopener noreferrer">Namespace Costs</a></li>
          <li><a href="http://localhost:8000/api/v1/recommendations/" target="_blank" rel="noopener noreferrer">Recommendations</a></li>
          <li><a href="http://localhost:8000/api/v1/analytics/comparisons" target="_blank" rel="noopener noreferrer">Cost Comparisons</a></li>
        </ul>
      </div>
      
      <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f0f8ff', borderRadius: '5px' }}>
        <h2>💡 Next Steps</h2>
        <p>This is a demo version of CloudCostGuard. To run the full version:</p>
        <ol>
          <li>Install Docker Desktop</li>
          <li>Run <code>docker-compose up -d</code></li>
          <li>Configure Azure credentials</li>
          <li>Set up Prometheus for Kubernetes metrics</li>
        </ol>
      </div>
      
      <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#e8f5e8', borderRadius: '5px' }}>
        <h2>🎯 Demo Features</h2>
        <p>The backend demo server provides mock data for:</p>
        <ul>
          <li>Cost overview and breakdown</li>
          <li>Namespace-wise cost allocation</li>
          <li>Optimization recommendations</li>
          <li>Month-over-month cost comparisons</li>
          <li>Azure subscription and resource group cost analysis</li>
        </ul>
      </div>
    </div>
  );
}

export default App;
