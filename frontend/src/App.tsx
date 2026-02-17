import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Overview from './pages/Overview';
import Recommendations from './pages/Recommendations';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/costs" element={<div>Cost Analysis Page - Coming Soon</div>} />
          <Route path="/analytics" element={<div>Analytics Page - Coming Soon</div>} />
          <Route path="/settings" element={<div>Settings Page - Coming Soon</div>} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
