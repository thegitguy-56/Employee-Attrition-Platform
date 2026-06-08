// Navbar.jsx — top bar showing the current page title and user info
import { useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// Map URL paths to page titles
const pageTitles = {
  '/dashboard':  'Dashboard',
  '/employees':  'Employee Management',
  '/prediction': 'Attrition Prediction',
  '/analytics':  'Analytics',
  '/reports':    'Reports',
  '/settings':   'Settings',
};

export default function Navbar() {
  const { pathname } = useLocation();
  const { user } = useAuth();
  const title = pageTitles[pathname] ?? 'HR Analytics';

  return (
    <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
      <h1 className="text-xl font-bold text-slate-800">{title}</h1>
      <div className="flex items-center gap-4">
        {/* Notification bell placeholder */}
        <button className="w-9 h-9 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 hover:bg-slate-200 transition-colors">
          🔔
        </button>
        {/* User badge */}
        <div className="flex items-center gap-2 bg-slate-100 rounded-full px-3 py-1.5">
          <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center text-white text-xs font-bold uppercase">
            {user?.full_name?.[0] ?? 'U'}
          </div>
          <span className="text-sm font-medium text-slate-700">{user?.full_name ?? 'User'}</span>
          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full capitalize">
            {user?.role?.replace('_', ' ') ?? 'HR'}
          </span>
        </div>
      </div>
    </header>
  );
}
