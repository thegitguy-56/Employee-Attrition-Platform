// DashboardPage.jsx — the main overview screen after login
// Shows: 4 stat cards, 2 charts (bar + pie), top-5 high-risk employee table

import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import StatCard from '../components/StatCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { getOverview, getByDepartment, getTopRisk } from '../api/analyticsApi';


export default function DashboardPage() {
  const [overview,    setOverview]    = useState(null);
  const [departments, setDepartments] = useState([]);
  const [topRisk,     setTopRisk]     = useState([]);
  const [loading,     setLoading]     = useState(true);
  const [error,       setError]       = useState('');

  useEffect(() => {
    const fetchAll = async () => {
      try {
        // Fire all 3 API calls at the same time for speed
        const [ov, dept, risk] = await Promise.all([
          getOverview(),
          getByDepartment(),
          getTopRisk(),
        ]);
        setOverview(ov);
        setDepartments(dept);
        setTopRisk(risk);
      } catch (err) {
        setError('Failed to load dashboard data. Is the backend running?');
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error)   return <ErrorMessage message={error} />;

  // Build pie chart data from overview
  const pieData = overview
    ? [
        { name: 'Low Risk',    value: overview.low_risk    ?? 0 },
        { name: 'Medium Risk', value: overview.medium_risk ?? 0 },
        { name: 'High Risk',   value: overview.high_risk   ?? 0 },
      ]
    : [];

  return (
    <div className="space-y-6">
      {/* ─── Row 1: Stat Cards ─── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard
          title="Total Employees"
          value={overview?.total_employees?.toLocaleString()}
          subtitle="Active workforce"
          color="blue"
          icon="users"
        />
        <StatCard
          title="High Risk Employees"
          value={overview?.high_risk}
          subtitle="Risk score > 70%"
          color="red"
          icon="alert"
        />
        <StatCard
          title="Avg Risk Score"
          value={overview?.average_risk_score ? `${overview.average_risk_score}%` : '—'}
          subtitle="Across all employees"
          color="yellow"
          icon="chart"
        />
        <StatCard
          title="Predictions Today"
          value={overview?.predictions_today ?? 0}
          subtitle="Analyses run today"
          color="green"
          icon="prediction"
        />
      </div>

      {/* ─── Row 2: Charts ─── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar chart — attrition risk by department */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">Risk Score by Department</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={departments} margin={{ top: 0, right: 10, left: -10, bottom: 0 }}>
              <XAxis dataKey="department" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip
                formatter={(val) => [`${val}%`, 'Avg Risk']}
                contentStyle={{ fontSize: 12, borderRadius: 8 }}
              />
              <Bar dataKey="avg_risk_score" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Donut chart — risk level distribution */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">Risk Level Distribution</h2>
          {(() => {
            const total = pieData.reduce((s, d) => s + d.value, 0);
            const COLORS = { 'Low Risk': '#22c55e', 'Medium Risk': '#f59e0b', 'High Risk': '#ef4444' };
            return (
              <div className="flex flex-col items-center gap-5">
                {/* Donut with centered label */}
                <div className="relative">
                  <ResponsiveContainer width={220} height={220}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%" cy="50%"
                        innerRadius={68} outerRadius={100}
                        dataKey="value"
                        strokeWidth={2}
                        stroke="#fff"
                        paddingAngle={pieData.filter(d => d.value > 0).length > 1 ? 3 : 0}
                      >
                        {pieData.map((entry, i) => (
                          <Cell key={i} fill={COLORS[entry.name]} />
                        ))}
                      </Pie>
                      <Tooltip
                        formatter={(val, name) => [`${val} employees (${total ? Math.round(val / total * 100) : 0}%)`, name]}
                        contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e2e8f0' }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                  {/* Centered text inside donut */}
                  <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                    <span className="text-3xl font-bold text-slate-800">{total}</span>
                    <span className="text-xs text-slate-400 mt-0.5">employees</span>
                  </div>
                </div>
                {/* Custom legend */}
                <div className="w-full grid grid-cols-3 gap-2">
                  {[
                    { name: 'High Risk',   color: '#ef4444', bg: 'bg-red-50',    text: 'text-red-700'    },
                    { name: 'Medium Risk', color: '#f59e0b', bg: 'bg-yellow-50', text: 'text-yellow-700' },
                    { name: 'Low Risk',    color: '#22c55e', bg: 'bg-green-50',  text: 'text-green-700'  },
                  ].map(({ name, bg, text }) => {
                    const d = pieData.find(p => p.name === name);
                    const val = d?.value ?? 0;
                    const pct = total ? Math.round(val / total * 100) : 0;
                    return (
                      <div key={name} className={`${bg} rounded-lg p-2.5 text-center`}>
                        <p className={`text-xl font-bold ${text}`}>{val}</p>
                        <p className={`text-xs font-medium ${text} opacity-80`}>{pct}%</p>
                        <p className="text-xs text-slate-500 mt-0.5">{name}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })()}
        </div>

      </div>

      {/* ─── Row 3: Top 5 High-Risk Employees ─── */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm">
        <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-700">Top High-Risk Employees</h2>
          <a href="/employees" className="text-xs text-blue-600 hover:underline">View all →</a>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                {['Employee', 'Department', 'Job Role', 'Risk Score', 'Recommendation'].map((h) => (
                  <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {topRisk.slice(0, 5).map((emp, i) => (
                <tr key={i} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-800">
                    {emp.first_name} {emp.last_name}
                  </td>
                  <td className="px-4 py-3 text-slate-600">{emp.department}</td>
                  <td className="px-4 py-3 text-slate-600">{emp.job_role}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                      emp.risk_score > 70 ? 'bg-red-100 text-red-700'
                      : emp.risk_score > 40 ? 'bg-yellow-100 text-yellow-700'
                      : 'bg-green-100 text-green-700'
                    }`}>
                      {emp.risk_score}%
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-500 text-xs max-w-xs truncate">
                    {emp.recommendation ?? '—'}
                  </td>
                </tr>
              ))}
              {!topRisk.length && (
                <tr>
                  <td colSpan={5} className="text-center py-8 text-slate-400 text-sm">
                    No predictions yet. Run a prediction first.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
