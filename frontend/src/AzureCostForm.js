import React, { useState } from 'react';

const AzureCostForm = () => {
  const [credentials, setCredentials] = useState({
    subscriptionId: '',
    clientId: '',
    clientSecret: '',
    tenantId: '',
    resourceGroup: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [costData, setCostData] = useState(null);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCredentials(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setCostData(null);

    try {
      // Call the backend API with Azure credentials
      const formData = new URLSearchParams();
      formData.append('subscriptionId', credentials.subscriptionId);
      formData.append('clientId', credentials.clientId);
      formData.append('clientSecret', credentials.clientSecret);
      formData.append('tenantId', credentials.tenantId);
      formData.append('resourceGroup', credentials.resourceGroup);

      const response = await fetch('http://localhost:8000/api/v1/azure/cost-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString()
      });

      if (!response.ok) {
        throw new Error('Failed to fetch cost data');
      }

      const data = await response.json();
      
      if (data.error) {
        setError(data.error);
      } else {
        setCostData(data);
      }
    } catch (err) {
      setError('Failed to fetch cost data. Please check your credentials and try again.');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <h2 style={{ color: '#2563eb', marginBottom: '30px' }}>
        ☁️ Azure Cost Analysis
      </h2>
      
      {/* Input Form */}
      <div style={{ 
        backgroundColor: '#f8fafc', 
        padding: '25px', 
        borderRadius: '10px', 
        marginBottom: '30px',
        border: '1px solid #e2e8f0'
      }}>
        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
                Subscription ID:
              </label>
              <input
                type="text"
                name="subscriptionId"
                value={credentials.subscriptionId}
                onChange={handleInputChange}
                placeholder="e.g., 12345678-1234-1234-1234-123456789012"
                required
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #d1d5db',
                  borderRadius: '5px',
                  fontSize: '14px'
                }}
              />
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
                Client ID:
              </label>
              <input
                type="text"
                name="clientId"
                value={credentials.clientId}
                onChange={handleInputChange}
                placeholder="Azure AD Application ID"
                required
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #d1d5db',
                  borderRadius: '5px',
                  fontSize: '14px'
                }}
              />
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
                Client Secret:
              </label>
              <input
                type="password"
                name="clientSecret"
                value={credentials.clientSecret}
                onChange={handleInputChange}
                placeholder="Azure AD Application Secret"
                required
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #d1d5db',
                  borderRadius: '5px',
                  fontSize: '14px'
                }}
              />
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
                Tenant ID:
              </label>
              <input
                type="text"
                name="tenantId"
                value={credentials.tenantId}
                onChange={handleInputChange}
                placeholder="Azure AD Tenant ID"
                required
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #d1d5db',
                  borderRadius: '5px',
                  fontSize: '14px'
                }}
              />
            </div>
          </div>
          
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
              Resource Group:
            </label>
            <input
              type="text"
              name="resourceGroup"
              value={credentials.resourceGroup}
              onChange={handleInputChange}
              placeholder="e.g., production-rg"
              required
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #d1d5db',
                borderRadius: '5px',
                fontSize: '14px'
              }}
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            style={{
              backgroundColor: loading ? '#9ca3af' : '#2563eb',
              color: 'white',
              padding: '12px 30px',
              border: 'none',
              borderRadius: '5px',
              fontSize: '16px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: 'bold'
            }}
          >
            {loading ? '🔄 Analyzing Costs...' : '📊 Get Cost Analysis'}
          </button>
        </form>
      </div>

      {/* Error Message */}
      {error && (
        <div style={{
          backgroundColor: '#fee2e2',
          color: '#dc2626',
          padding: '15px',
          borderRadius: '5px',
          marginBottom: '20px',
          border: '1px solid #fecaca'
        }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Cost Results */}
      {costData && (
        <div style={{ backgroundColor: '#f0fdf4', padding: '25px', borderRadius: '10px', border: '1px solid #bbf7d0' }}>
          <h3 style={{ color: '#16a34a', marginBottom: '20px' }}>
            💰 Cost Analysis Results
          </h3>
          
          {/* Summary Card */}
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            marginBottom: '20px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <p style={{ margin: '0', color: '#6b7280', fontSize: '14px' }}>
                  Total Cost ({costData.period})
                </p>
                <p style={{ 
                  margin: '5px 0 0 0', 
                  fontSize: '32px', 
                  fontWeight: 'bold', 
                  color: '#111827' 
                }}>
                  ${costData.totalCost.toFixed(2)} {costData.currency}
                </p>
              </div>
              <div style={{ textAlign: 'right' }}>
                <p style={{ margin: '0', color: '#6b7280', fontSize: '12px' }}>
                  Subscription: {costData.subscriptionId.substring(0, 8)}...
                </p>
                <p style={{ margin: '5px 0 0 0', color: '#6b7280', fontSize: '12px' }}>
                  Resource Group: {costData.resourceGroup}
                </p>
              </div>
            </div>
          </div>

          {/* Cost Breakdown */}
          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ color: '#374151', marginBottom: '15px' }}>Cost Breakdown</h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
              {Object.entries(costData.breakdown).map(([category, cost]) => (
                <div key={category} style={{
                  backgroundColor: 'white',
                  padding: '15px',
                  borderRadius: '8px',
                  border: '1px solid #e5e7eb'
                }}>
                  <p style={{ margin: '0', color: '#6b7280', fontSize: '12px', textTransform: 'capitalize' }}>
                    {category}
                  </p>
                  <p style={{ margin: '5px 0 0 0', fontSize: '18px', fontWeight: 'bold', color: '#111827' }}>
                    ${cost.toFixed(2)}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Top Resources */}
          <div>
            <h4 style={{ color: '#374151', marginBottom: '15px' }}>Top Resources</h4>
            <div style={{ backgroundColor: 'white', borderRadius: '8px', overflow: 'hidden' }}>
              {costData.resources.map((resource, index) => (
                <div key={index} style={{
                  padding: '15px',
                  borderBottom: index < costData.resources.length - 1 ? '1px solid #e5e7eb' : 'none',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <div>
                    <p style={{ margin: '0', fontWeight: 'bold', color: '#111827' }}>
                      {resource.name}
                    </p>
                    <p style={{ margin: '5px 0 0 0', color: '#6b7280', fontSize: '14px' }}>
                      {resource.type}
                    </p>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <p style={{ margin: '0', fontSize: '16px', fontWeight: 'bold', color: '#111827' }}>
                      ${resource.cost.toFixed(2)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <p style={{ 
            margin: '20px 0 0 0', 
            color: '#6b7280', 
            fontSize: '12px',
            textAlign: 'center' 
          }}>
            Last updated: {new Date(costData.lastUpdated).toLocaleString()}
          </p>
        </div>
      )}
    </div>
  );
};

export default AzureCostForm;
