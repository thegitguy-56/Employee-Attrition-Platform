import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid, Legend } from 'recharts';
import { getByDepartment, getBySatisfaction, getSalaryAnalysis, getTopRisk, getFeatureImportance } from '../api/analyticsApi';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

export default function AnalyticsPage() {
  const [dept, setDept]     = useState([]);
  const [sat, setSat]       = useState([]);
  const [salary, setSalary] = useState([]);
  const [topRisk, setTop]   = useState([]);
  const [fi, setFI]         = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState('');

  useEffect(() => {
    Promise.all([getByDepartment(), getBySatisfaction(), getSalaryAnalysis(), getTopRisk(), getFeatureImportance()])
      .then(([d, s, sal, t, f]) => { setDept(d); setSat(s); setSalary(sal); setTop(t); setFI(f); })
      .catch(() => setError('Failed to load analytics. Is the backend running?'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error)   return <ErrorMessage message={error} />;

  const Section = ({ title, children }) => (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
      <h2 className="font-semibold text-slate-800 mb-4">{title}</h2>
      {children}
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Section title="Average Risk Score by Department">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={dept}><XAxis dataKey="department" tick={{fontSize:11}} /><YAxis tick={{fontSize:11}} /><Tooltip formatter={v=>[`${v}%`,'Risk']} /><Bar dataKey="avg_risk_score" fill="#3b82f6" radius={[4,4,0,0]} /></BarChart>
          </ResponsiveContainer>
        </Section>

        <Section title="Job Satisfaction vs Attrition Risk">
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={sat}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="satisfaction" tick={{fontSize:11}} label={{value:'Satisfaction Level',position:'insideBottom',offset:-2,fontSize:11}} /><YAxis tick={{fontSize:11}} /><Tooltip formatter={v=>[`${v}%`,'Risk']} /><Line type="monotone" dataKey="avg_risk_score" stroke="#ef4444" strokeWidth={2} dot={{ r:4 }} /></LineChart>
          </ResponsiveContainer>
        </Section>

        <Section title="Salary: High-Risk vs Low-Risk Employees">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={salary}><XAxis dataKey="department" tick={{fontSize:10}} /><YAxis tick={{fontSize:11}} /><Tooltip formatter={v=>[`$${v?.toLocaleString()}`,'Avg Income']} /><Legend /><Bar dataKey="high_risk_income" name="High Risk" fill="#ef4444" radius={[4,4,0,0]} /><Bar dataKey="low_risk_income" name="Low Risk" fill="#22c55e" radius={[4,4,0,0]} /></BarChart>
          </ResponsiveContainer>
        </Section>

        <Section title="Top Feature Importances">
          <div className="space-y-2">
            {(fi.slice ? fi.slice(0,10) : []).map((f, i) => (
              <div key={i} className="flex items-center gap-3">
                <span className="text-xs text-slate-500 w-40 truncate">{f.feature}</span>
                <div className="flex-1 bg-slate-100 rounded-full h-2">
                  <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${Math.round((f.importance ?? 0) * 100)}%` }}></div>
                </div>
                <span className="text-xs font-medium text-slate-600 w-10 text-right">{((f.importance ?? 0)*100).toFixed(1)}%</span>
              </div>
            ))}
            {fi.length === 0 && <p className="text-sm text-slate-400 text-center py-4">No feature importance data. Run the ML pipeline first.</p>}
          </div>
        </Section>
      </div>

      {/* High-risk employee table */}
      <Section title="High-Risk Employees (Risk > 70%)">
        <div className="overflow-x-auto rounded-lg border border-slate-200">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>{['Employee','Department','Risk Score','Key Factor'].map(h=><th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">{h}</th>)}</tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {topRisk.filter(e => e.risk_score > 70).slice(0,20).map((e, i) => (
                <tr key={i} className="hover:bg-red-50/30">
                  <td className="px-4 py-3 font-medium text-slate-800">{e.first_name} {e.last_name}</td>
                  <td className="px-4 py-3 text-slate-600">{e.department}</td>
                  <td className="px-4 py-3"><span className="px-2.5 py-0.5 bg-red-100 text-red-700 rounded-full text-xs font-bold">{e.risk_score}%</span></td>
                  <td className="px-4 py-3 text-slate-500 text-xs">{e.key_factor ?? '—'}</td>
                </tr>
              ))}
              {topRisk.filter(e=>e.risk_score>70).length===0 && <tr><td colSpan={4} className="text-center py-8 text-slate-400">No high-risk employees found. Run predictions first.</td></tr>}
            </tbody>
          </table>
        </div>
      </Section>
    </div>
  );
}
