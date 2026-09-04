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
          <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}><path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg>
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
