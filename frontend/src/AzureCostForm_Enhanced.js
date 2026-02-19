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
  const [focusedField, setFocusedField] = useState(null);

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
      // Call backend API with Azure credentials
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

  const styles = {
    container: {
      maxWidth: '900px',
      margin: '0 auto',
      padding: '20px',
      background: 'rgba(255, 255, 255, 0.95)',
      backdropFilter: 'blur(10px)',
      borderRadius: '25px',
      boxShadow: '0 25px 50px rgba(0,0,0,0.15)',
      border: '1px solid rgba(255,255,255,0.3)',
      animation: 'fadeInUp 1s ease-out'
    },
    header: {
      textAlign: 'center',
      marginBottom: '35px',
      color: '#2563eb'
    },
    title: {
      fontSize: '2.5rem',
      fontWeight: '700',
      margin: '0 0 10px 0',
      background: 'linear-gradient(135deg, #667eea, #764ba2)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      backgroundClip: 'text'
    },
    subtitle: {
      fontSize: '1.1rem',
      color: '#6c757d',
      margin: '0',
      fontWeight: '400'
    },
    form: {
      marginBottom: '30px'
    },
    formGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
      gap: '25px',
      marginBottom: '25px'
    },
    formGroup: {
      position: 'relative'
    },
    label: {
      display: 'block',
      marginBottom: '8px',
      fontWeight: '600',
      color: '#374151',
      fontSize: '0.95rem',
      transition: 'color 0.3s ease'
    },
    labelFocused: {
      color: '#2563eb'
    },
    input: {
      width: '100%',
      padding: '14px 16px',
      border: '2px solid #e5e7eb',
      borderRadius: '12px',
      fontSize: '15px',
      transition: 'all 0.3s ease',
      backgroundColor: '#ffffff',
      boxSizing: 'border-box'
    },
    inputFocused: {
      borderColor: '#2563eb',
      boxShadow: '0 0 0 3px rgba(37, 99, 235, 0.1)',
      transform: 'translateY(-2px)'
    },
    inputError: {
      borderColor: '#dc2626',
      boxShadow: '0 0 0 3px rgba(220, 38, 38, 0.1)'
    },
    submitButton: {
      width: '100%',
      padding: '16px 32px',
      background: loading ? '#9ca3af' : 'linear-gradient(135deg, #2563eb, #1d4ed8)',
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      fontSize: '18px',
      fontWeight: '600',
      cursor: loading ? 'not-allowed' : 'pointer',
      transition: 'all 0.3s ease',
      boxShadow: '0 10px 25px rgba(37, 99, 235, 0.3)',
      textTransform: 'uppercase',
      letterSpacing: '0.5px',
      position: 'relative',
      overflow: 'hidden'
    },
    submitButtonHover: {
      transform: 'translateY(-3px)',
      boxShadow: '0 15px 35px rgba(37, 99, 235, 0.4)'
    },
    submitButtonLoading: {
      background: 'linear-gradient(135deg, #9ca3af, #6b7280)'
    },
    errorContainer: {
      backgroundColor: '#fee2e2',
      color: '#dc2626',
      padding: '18px 24px',
      borderRadius: '12px',
      marginBottom: '25px',
      border: '1px solid #fecaca',
      borderLeft: '4px solid #dc2626',
      animation: 'shake 0.5s ease-in-out'
    },
    resultsContainer: {
      background: 'linear-gradient(135deg, #f0fdf4, #dcfce7)',
      padding: '30px',
      borderRadius: '20px',
      border: '1px solid #bbf7d0',
      boxShadow: '0 20px 40px rgba(34, 197, 94, 0.1)',
      animation: 'fadeInUp 0.8s ease-out'
    },
    resultsHeader: {
      color: '#16a34a',
      marginBottom: '25px',
      textAlign: 'center'
    },
    resultsTitle: {
      fontSize: '2rem',
      fontWeight: '700',
      margin: '0 0 10px 0'
    },
    summaryCard: {
      background: 'white',
      padding: '25px',
      borderRadius: '16px',
      marginBottom: '25px',
      boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
      border: '1px solid #e5e7eb'
    },
    summaryContent: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      flexWrap: 'wrap'
    },
    summaryLeft: {
      flex: '1',
      minWidth: '200px'
    },
    summaryRight: {
      textAlign: 'right',
      minWidth: '150px'
    },
    totalCost: {
      fontSize: '2.5rem',
      fontWeight: '800',
      color: '#111827',
      margin: '5px 0',
      background: 'linear-gradient(135deg, #059669, #047857)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      backgroundClip: 'text'
    },
    breakdownGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: '20px',
      marginBottom: '25px'
    },
    breakdownItem: {
      background: 'white',
      padding: '20px',
      borderRadius: '14px',
      border: '1px solid #e5e7eb',
      transition: 'all 0.3s ease',
      cursor: 'pointer'
    },
    breakdownItemHover: {
      transform: 'translateY(-5px)',
      boxShadow: '0 15px 35px rgba(0,0,0,0.15)',
      borderColor: '#2563eb'
    },
    categoryLabel: {
      margin: '0',
      color: '#6b7280',
      fontSize: '0.9rem',
      fontWeight: '500',
      textTransform: 'capitalize',
      marginBottom: '8px'
    },
    categoryCost: {
      margin: '0',
      fontSize: '1.5rem',
      fontWeight: '700',
      color: '#111827'
    },
    resourcesTitle: {
      color: '#374151',
      marginBottom: '20px',
      fontSize: '1.3rem',
      fontWeight: '600'
    },
    resourceList: {
      background: 'white',
      borderRadius: '16px',
      overflow: 'hidden',
      border: '1px solid #e5e7eb'
    },
    resourceItem: {
      padding: '20px 25px',
      borderBottom: '1px solid #f3f4f6',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      transition: 'background-color 0.3s ease'
    },
    resourceItemHover: {
      backgroundColor: '#f8fafc'
    },
    resourceItemLast: {
      borderBottom: 'none'
    },
    resourceInfo: {
      flex: '1'
    },
    resourceName: {
      margin: '0',
      fontWeight: '600',
      color: '#111827',
      fontSize: '1.1rem'
    },
    resourceType: {
      margin: '5px 0 0 0',
      color: '#6b7280',
      fontSize: '0.9rem'
    },
    resourceCost: {
      fontSize: '1.3rem',
      fontWeight: '700',
      color: '#059669'
    },
    timestamp: {
      textAlign: 'center',
      marginTop: '20px',
      color: '#6b7280',
      fontSize: '0.85rem',
      fontStyle: 'italic'
    }
  };

  const [hoveredBreakdown, setHoveredBreakdown] = useState(null);
  const [hoveredResource, setHoveredResource] = useState(null);

  return (
    <div style={styles.container}>
      <style>
        {`
          @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
          }
          @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
          }
          input::placeholder { color: #9ca3af; }
          input:focus { outline: none; }
        `}
      </style>

      <div style={styles.header}>
        <h2 style={styles.title}>Azure Cost Analysis</h2>
        <p style={styles.subtitle}>Enter your Azure credentials to get detailed cost insights</p>
      </div>

      <form style={styles.form} onSubmit={handleSubmit}>
        <div style={styles.formGrid}>
          {[
            { name: 'subscriptionId', label: 'Subscription ID', placeholder: '12345678-1234-1234-1234-123456789012', type: 'text' },
            { name: 'clientId', label: 'Client ID', placeholder: 'Azure AD Application ID', type: 'text' },
            { name: 'clientSecret', label: 'Client Secret', placeholder: 'Azure AD Application Secret', type: 'password' },
            { name: 'tenantId', label: 'Tenant ID', placeholder: 'Azure AD Tenant ID', type: 'text' },
            { name: 'resourceGroup', label: 'Resource Group', placeholder: 'e.g., production-rg', type: 'text' }
          ].map((field, index) => (
            <div key={field.name} style={styles.formGroup}>
              <label 
                style={{
                  ...styles.label,
                  ...(focusedField === field.name ? styles.labelFocused : {})
                }}
              >
                {field.label}
              </label>
              <input
                type={field.type}
                name={field.name}
                value={credentials[field.name]}
                onChange={handleInputChange}
                placeholder={field.placeholder}
                required
                style={{
                  ...styles.input,
                  ...(focusedField === field.name ? styles.inputFocused : {}),
                  ...(error ? styles.inputError : {})
                }}
                onFocus={() => setFocusedField(field.name)}
                onBlur={() => setFocusedField(null)}
              />
            </div>
          ))}
        </div>
        
        <button
          type="submit"
          disabled={loading}
          style={{
            ...styles.submitButton,
            ...(loading ? styles.submitButtonLoading : {})
          }}
        >
          {loading ? 'Analyzing Costs...' : 'Get Cost Analysis'}
        </button>
      </form>

      {error && (
        <div style={styles.errorContainer}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {costData && (
        <div style={styles.resultsContainer}>
          <div style={styles.resultsHeader}>
            <h3 style={styles.resultsTitle}>Cost Analysis Results</h3>
            <p>Detailed breakdown for your Azure resources</p>
          </div>
          
          <div style={styles.summaryCard}>
            <div style={styles.summaryContent}>
              <div style={styles.summaryLeft}>
                <p style={{ margin: '0', color: '#6b7280', fontSize: '0.9rem' }}>
                  Total Cost ({costData.period})
                </p>
                <p style={styles.totalCost}>
                  ${costData.totalCost.toFixed(2)} {costData.currency}
                </p>
              </div>
              <div style={styles.summaryRight}>
                <p style={{ margin: '0', color: '#6b7280', fontSize: '0.85rem' }}>
                  Subscription: {costData.subscriptionId.substring(0, 8)}...
                </p>
                <p style={{ margin: '5px 0 0 0', color: '#6b7280', fontSize: '0.85rem' }}>
                  Resource Group: {costData.resourceGroup}
                </p>
              </div>
            </div>
          </div>

          <div>
            <h4 style={styles.resourcesTitle}>Cost Breakdown by Category</h4>
            <div style={styles.breakdownGrid}>
              {Object.entries(costData.breakdown).map(([category, cost]) => (
                <div
                  key={category}
                  style={{
                    ...styles.breakdownItem,
                    ...(hoveredBreakdown === category ? styles.breakdownItemHover : {})
                  }}
                  onMouseEnter={() => setHoveredBreakdown(category)}
                  onMouseLeave={() => setHoveredBreakdown(null)}
                >
                  <p style={styles.categoryLabel}>{category.replace('_', ' ')}</p>
                  <p style={styles.categoryCost}>${cost.toFixed(2)}</p>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 style={styles.resourcesTitle}>Top Resources</h4>
            <div style={styles.resourceList}>
              {costData.resources.map((resource, index) => (
                <div
                  key={index}
                  style={{
                    ...styles.resourceItem,
                    ...(hoveredResource === index ? styles.resourceItemHover : {}),
                    ...(index === costData.resources.length - 1 ? styles.resourceItemLast : {})
                  }}
                  onMouseEnter={() => setHoveredResource(index)}
                  onMouseLeave={() => setHoveredResource(null)}
                >
                  <div style={styles.resourceInfo}>
                    <p style={styles.resourceName}>{resource.name}</p>
                    <p style={styles.resourceType}>{resource.type}</p>
                  </div>
                  <div style={styles.resourceCost}>
                    ${resource.cost.toFixed(2)}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <p style={styles.timestamp}>
            Last updated: {new Date(costData.lastUpdated).toLocaleString()}
          </p>
        </div>
      )}
    </div>
  );
};

export default AzureCostForm;
