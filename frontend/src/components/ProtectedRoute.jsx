// ProtectedRoute.jsx — a security gate for pages that need login
// If user is NOT logged in → redirect to /login
// If user IS logged in → show the page normally

import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import LoadingSpinner from './LoadingSpinner';

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  // While checking localStorage on startup, show a spinner
  if (loading) return <LoadingSpinner fullScreen />;

  // Not logged in? Send to login page
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  // Logged in? Render the child page/component
  return children;
}
