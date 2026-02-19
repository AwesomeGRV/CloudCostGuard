import React, { useState, useEffect } from 'react';
import AzureCostForm from './AzureCostForm_Enhanced';

const App = () => {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const styles = {
    app: {
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #ff8c42 0%, #ff6b35 100%)',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      color: '#333'
    },
    container: {
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '20px'
    },
    header: {
      textAlign: 'center',
      marginBottom: '40px',
      color: 'white',
      animation: 'fadeInDown 1s ease-out'
    },
    title: {
      fontSize: '3.5rem',
      fontWeight: '700',
      margin: '0 0 10px 0',
      textShadow: '0 4px 6px rgba(0,0,0,0.3)',
      background: 'linear-gradient(45deg, #ff8c42, #ff6b35)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      backgroundClip: 'text'
    },
    subtitle: {
      fontSize: '1.3rem',
      margin: '0',
      opacity: '0.95',
      fontWeight: '300'
    },
    statusCard: {
      background: 'rgba(255, 255, 255, 0.95)',
      backdropFilter: 'blur(10px)',
      borderRadius: '20px',
      padding: '30px',
      marginBottom: '30px',
      boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
      border: '1px solid rgba(255,255,255,0.2)',
      animation: 'fadeInUp 1s ease-out'
    },
    statusGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
      gap: '20px',
      marginBottom: '20px'
    },
    statusItem: {
      display: 'flex',
      alignItems: 'center',
      padding: '15px',
      background: 'linear-gradient(135deg, #f8f9fa, #e9ecef)',
      borderRadius: '12px',
      transition: 'transform 0.3s ease, box-shadow 0.3s ease'
    },
    statusItemHover: {
      transform: 'translateY(-5px)',
      boxShadow: '0 10px 25px rgba(0,0,0,0.15)'
    },
    statusIcon: {
      fontSize: '1.5rem',
      marginRight: '15px',
      width: '40px',
      height: '40px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: '50%',
      background: 'linear-gradient(135deg, #ff8c42, #ff6b35)',
      color: 'white'
    },
    statusText: {
      flex: 1
    },
    statusLabel: {
      fontSize: '0.9rem',
      color: '#6c757d',
      margin: '0 0 5px 0',
      fontWeight: '500'
    },
    statusValue: {
      fontSize: '1.1rem',
      color: '#212529',
      margin: '0',
      fontWeight: '600'
    },
    endpointsCard: {
      background: 'rgba(255, 255, 255, 0.95)',
      backdropFilter: 'blur(10px)',
      borderRadius: '20px',
      padding: '30px',
      marginBottom: '30px',
      boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
      border: '1px solid rgba(255,255,255,0.2)',
      animation: 'fadeInUp 1.2s ease-out'
    },
    endpointsGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
      gap: '15px'
    },
    endpointItem: {
      padding: '20px',
      background: 'linear-gradient(135deg, #ffffff, #f8f9fa)',
      borderRadius: '15px',
      border: '1px solid #e9ecef',
      transition: 'all 0.3s ease',
      cursor: 'pointer'
    },
    endpointItemHover: {
      transform: 'scale(1.05)',
      boxShadow: '0 15px 30px rgba(0,0,0,0.15)',
      borderColor: '#ff6b35'
    },
    endpointTitle: {
      fontSize: '1.1rem',
      fontWeight: '600',
      color: '#ff6b35',
      margin: '0 0 10px 0',
      display: 'flex',
      alignItems: 'center'
    },
    endpointUrl: {
      fontSize: '0.9rem',
      color: '#6c757d',
      margin: '0',
      fontFamily: 'Monaco, Consolas, "Courier New", monospace',
      background: '#f8f9fa',
      padding: '5px 10px',
      borderRadius: '5px',
      display: 'inline-block'
    },
    infoCard: {
      background: 'rgba(255, 255, 255, 0.95)',
      backdropFilter: 'blur(10px)',
      borderRadius: '20px',
      padding: '30px',
      marginBottom: '30px',
      boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
      border: '1px solid rgba(255,255,255,0.2)',
      animation: 'fadeInUp 1.4s ease-out'
    },
    infoGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
      gap: '20px'
    },
    infoSection: {
      padding: '20px'
    },
    infoTitle: {
      fontSize: '1.3rem',
      fontWeight: '600',
      color: '#495057',
      margin: '0 0 15px 0',
      display: 'flex',
      alignItems: 'center'
    },
    infoContent: {
      fontSize: '1rem',
      lineHeight: '1.6',
      color: '#6c757d'
    },
    footer: {
      textAlign: 'center',
      padding: '30px 20px',
      color: 'white',
      opacity: '0.9'
    },
    timeDisplay: {
      fontSize: '0.9rem',
      opacity: '0.8'
    }
  };

  const endpoints = [
    { name: 'Health Check', url: 'http://localhost:8000/health', icon: '•' },
    { name: 'Cost Overview', url: 'http://localhost:8000/api/v1/costs/overview', icon: '•' },
    { name: 'Namespace Costs', url: 'http://localhost:8000/api/v1/costs/namespaces', icon: '•' },
    { name: 'Recommendations', url: 'http://localhost:8000/api/v1/recommendations/', icon: '•' },
    { name: 'Cost Comparisons', url: 'http://localhost:8000/api/v1/analytics/comparisons', icon: '•' }
  ];

  const [hoveredStatus, setHoveredStatus] = useState(null);
  const [hoveredEndpoint, setHoveredEndpoint] = useState(null);

  return (
    <div style={styles.app}>
      <style>
        {`
          @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-30px); }
            to { opacity: 1; transform: translateY(0); }
          }
          @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
          }
          a { text-decoration: none; color: inherit; }
          a:hover { text-decoration: underline; }
        `}
      </style>
      
      <div style={styles.container}>
        <header style={styles.header}>
          <h1 style={styles.title}>CloudCostGuard</h1>
          <p style={styles.subtitle}>Enterprise FinOps Platform for Cloud Cost Management</p>
          <div style={styles.timeDisplay}>
            {currentTime.toLocaleString()}
          </div>
        </header>

        <div style={styles.statusCard}>
          <h2 style={{ fontSize: '1.8rem', fontWeight: '600', marginBottom: '25px', color: '#495057' }}>
            System Status
          </h2>
          <div style={styles.statusGrid}>
            {[
              { label: 'Backend Server', value: 'Running on port 8000', icon: '•' },
              { label: 'Frontend Server', value: 'Running on port 3000', icon: '•' },
              { label: 'API Health', value: 'All systems healthy', icon: '•' },
              { label: 'Database', value: 'Connected and ready', icon: '•' }
            ].map((item, index) => (
              <div
                key={index}
                style={{
                  ...styles.statusItem,
                  ...(hoveredStatus === index ? styles.statusItemHover : {})
                }}
                onMouseEnter={() => setHoveredStatus(index)}
                onMouseLeave={() => setHoveredStatus(null)}
              >
                <div style={styles.statusIcon}>{item.icon}</div>
                <div style={styles.statusText}>
                  <p style={styles.statusLabel}>{item.label}</p>
                  <p style={styles.statusValue}>{item.value}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <AzureCostForm />

        <div style={styles.endpointsCard}>
          <h2 style={{ fontSize: '1.8rem', fontWeight: '600', marginBottom: '25px', color: '#495057' }}>
            API Endpoints
          </h2>
          <div style={styles.endpointsGrid}>
            {endpoints.map((endpoint, index) => (
              <div
                key={index}
                style={{
                  ...styles.endpointItem,
                  ...(hoveredEndpoint === index ? styles.endpointItemHover : {})
                }}
                onMouseEnter={() => setHoveredEndpoint(index)}
                onMouseLeave={() => setHoveredEndpoint(null)}
                onClick={() => window.open(endpoint.url, '_blank')}
              >
                <h3 style={styles.endpointTitle}>
                  <span style={{ marginRight: '10px' }}>{endpoint.icon}</span>
                  {endpoint.name}
                </h3>
                <p style={styles.endpointUrl}>{endpoint.url}</p>
              </div>
            ))}
          </div>
        </div>

        <div style={styles.infoCard}>
          <div style={styles.infoGrid}>
            <div style={styles.infoSection}>
              <h3 style={styles.infoTitle}>
                <span style={{ marginRight: '10px' }}></span>
                Next Steps
              </h3>
              <div style={styles.infoContent}>
                <p>This is a demo version of CloudCostGuard. To run the full production version:</p>
                <ol style={{ paddingLeft: '20px', marginTop: '10px' }}>
                  <li style={{ marginBottom: '8px' }}>Install Docker Desktop</li>
                  <li style={{ marginBottom: '8px' }}>Run <code style={{ background: '#f8f9fa', padding: '2px 6px', borderRadius: '3px' }}>docker-compose up -d</code></li>
                  <li style={{ marginBottom: '8px' }}>Configure your Azure credentials</li>
                  <li style={{ marginBottom: '8px' }}>Set up Prometheus for Kubernetes metrics</li>
                </ol>
              </div>
            </div>
            
            <div style={styles.infoSection}>
              <h3 style={styles.infoTitle}>
                <span style={{ marginRight: '10px' }}></span>
                Demo Features
              </h3>
              <div style={styles.infoContent}>
                <p>The backend demo server provides mock data for:</p>
                <ul style={{ paddingLeft: '20px', marginTop: '10px' }}>
                  <li style={{ marginBottom: '5px' }}>Cost overview and breakdown</li>
                  <li style={{ marginBottom: '5px' }}>Namespace-wise cost allocation</li>
                  <li style={{ marginBottom: '5px' }}>Optimization recommendations</li>
                  <li style={{ marginBottom: '5px' }}>Month-over-month cost comparisons</li>
                  <li style={{ marginBottom: '5px' }}>Azure subscription and resource group analysis</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <footer style={styles.footer}>
          <p>© 2026 CloudCostGuard - Open-Source FinOps Platform</p>
          <p style={{ fontSize: '0.9rem', marginTop: '10px' }}>
            Built with passion by awesomeGRV using React, FastAPI, and modern web technologies
          </p>
        </footer>
      </div>
    </div>
  );
};

export default App;
