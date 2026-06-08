// Sidebar.jsx — the dark navigation panel on the left
// Shows nav links, highlights the active page, shows user info at the bottom

import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const navItems = [
  { path: '/dashboard',   label: 'Dashboard',   icon: '📊' },
  { path: '/employees',   label: 'Employees',   icon: '👥' },
  { path: '/prediction',  label: 'Predictions', icon: '🔮' },
  { path: '/analytics',   label: 'Analytics',   icon: '📈' },
  { path: '/reports',     label: 'Reports',     icon: '📄' },
  { path: '/settings',    label: 'Settings',    icon: '⚙️'  },
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="w-64 min-h-screen flex flex-col" style={{ backgroundColor: '#0f172a' }}>
      {/* Logo / App title */}
      <div className="px-6 py-5 border-b border-slate-700">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-blue-500 rounded-lg flex items-center justify-center text-white font-bold text-lg">
            HR
          </div>
          <div>
            <p className="text-white font-semibold text-sm leading-tight">HR Analytics</p>
            <p className="text-slate-400 text-xs">Attrition Platform</p>
          </div>
        </div>
      </div>

      {/* Navigation links */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-300 hover:bg-slate-700 hover:text-white'
              }`
            }
          >
            <span className="text-base">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* User info + logout at the bottom */}
      <div className="px-4 py-4 border-t border-slate-700">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-8 h-8 bg-slate-600 rounded-full flex items-center justify-center text-white text-xs font-bold uppercase">
            {user?.full_name?.[0] ?? 'U'}
          </div>
          <div className="overflow-hidden">
            <p className="text-white text-xs font-medium truncate">{user?.full_name ?? 'User'}</p>
            <p className="text-slate-400 text-xs capitalize">{user?.role ?? 'hr_manager'}</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="w-full text-left px-3 py-2 rounded-lg text-sm text-slate-400 hover:bg-red-900 hover:text-red-300 transition-all flex items-center gap-2"
        >
          <span>🚪</span> Logout
        </button>
      </div>
    </aside>
  );
}
