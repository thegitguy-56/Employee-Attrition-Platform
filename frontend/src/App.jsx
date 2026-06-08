// App.jsx — the root component that sets up all routes
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';

// Pages
import LoginPage      from './pages/LoginPage';
import DashboardPage  from './pages/DashboardPage';
import EmployeesPage  from './pages/EmployeesPage';
import PredictionPage from './pages/PredictionPage';
import AnalyticsPage  from './pages/AnalyticsPage';
import ReportsPage    from './pages/ReportsPage';
import SettingsPage   from './pages/SettingsPage';

// Wrap a page with Layout (sidebar + navbar)
const Page = ({ children }) => (
  <ProtectedRoute>
    <Layout>{children}</Layout>
  </ProtectedRoute>
);

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        {/* Toast notifications — appears in top-right corner */}
        <Toaster position="top-right" toastOptions={{ duration: 3000 }} />

        <Routes>
          {/* Public route */}
          <Route path="/login" element={<LoginPage />} />

          {/* Redirect root to dashboard */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />

          {/* Protected routes — all wrapped in sidebar layout */}
          <Route path="/dashboard"  element={<Page><DashboardPage /></Page>} />
          <Route path="/employees"  element={<Page><EmployeesPage /></Page>} />
          <Route path="/prediction" element={<Page><PredictionPage /></Page>} />
          <Route path="/analytics"  element={<Page><AnalyticsPage /></Page>} />
          <Route path="/reports"    element={<Page><ReportsPage /></Page>} />
          <Route path="/settings"   element={<Page><SettingsPage /></Page>} />

          {/* Catch-all — redirect unknown URLs to dashboard */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
