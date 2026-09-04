// StatCard.jsx — a single metric card shown on the Dashboard
// Props:
//   title   — label like "Total Employees"
//   value   — the big number like "1,470"
//   subtitle — small text below like "Active workforce"
//   color   — "blue" | "red" | "yellow" | "green"
//   icon    — string key: "users" | "alert" | "chart" | "prediction"

const ICONS = {
  users: (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  ),
  alert: (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
  ),
  chart: (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  ),
  prediction: (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
  ),
};

export default function StatCard({ title, value, subtitle, color = 'blue', icon }) {
  const colorMap = {
    blue:   'bg-blue-50 text-blue-600 border-blue-100',
    red:    'bg-red-50 text-red-600 border-red-100',
    yellow: 'bg-yellow-50 text-yellow-600 border-yellow-100',
    green:  'bg-green-50 text-green-600 border-green-100',
  };

  const iconBg = {
    blue:   'bg-blue-100',
    red:    'bg-red-100',
    yellow: 'bg-yellow-100',
    green:  'bg-green-100',
  };

  const renderedIcon = ICONS[icon] ?? icon;

  return (
    <div className={`bg-white rounded-xl border p-5 shadow-sm hover:shadow-md transition-shadow ${colorMap[color]}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">{title}</p>
          <p className="text-3xl font-bold mt-1 text-slate-800">{value ?? '—'}</p>
          {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
        </div>
        {icon && (
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${iconBg[color]}`}>
            {renderedIcon}
          </div>
        )}
      </div>
    </div>
  );
}
