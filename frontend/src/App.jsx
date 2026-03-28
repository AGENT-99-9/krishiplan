import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import AssistantPage from './pages/AssistantPage';
import MarketplacePage from './pages/MarketplacePage';
import CommunityPage from './pages/CommunityPage';
import DashboardPage from './pages/DashboardPage';
import VendorDashboardPage from './pages/VendorDashboardPage';
import AdminDashboardPage from './pages/AdminDashboardPage';

import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />

        {/* Protected Routes */}
        <Route path="/assistant" element={
          <ProtectedRoute>
            <AssistantPage />
          </ProtectedRoute>
        } />
        <Route path="/marketplace" element={<MarketplacePage />} />
        <Route path="/community" element={
          <ProtectedRoute>
            <CommunityPage />
          </ProtectedRoute>
        } />
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        } />
        <Route path="/dashboard/*" element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        } />
        <Route path="/vendor-dashboard" element={
          <ProtectedRoute>
            <VendorDashboardPage />
          </ProtectedRoute>
        } />
        <Route path="/vendor-dashboard/*" element={
          <ProtectedRoute>
            <VendorDashboardPage />
          </ProtectedRoute>
        } />
        <Route path="/admin-dashboard" element={
          <ProtectedRoute>
            <AdminDashboardPage />
          </ProtectedRoute>
        } />

        {/* 404 Catch-all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
