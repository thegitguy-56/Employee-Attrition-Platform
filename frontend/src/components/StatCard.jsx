// StatCard.jsx — a single metric card shown on the Dashboard
// Props:
//   title   — label like "Total Employees"
//   value   — the big number like "1,470"
//   subtitle — small text below like "Active workforce"
//   color   — "blue" | "red" | "yellow" | "green"
//   icon    — emoji icon like "👥"

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

  return (
    <div className={`bg-white rounded-xl border p-5 shadow-sm hover:shadow-md transition-shadow ${colorMap[color]}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">{title}</p>
          <p className="text-3xl font-bold mt-1 text-slate-800">{value ?? '—'}</p>
          {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
        </div>
        {icon && (
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-xl ${iconBg[color]}`}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}
