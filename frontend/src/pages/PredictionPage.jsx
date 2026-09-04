import { useState } from 'react';
import { predictSingle, predictBatch } from '../api/predictionApi';
import { getAllEmployees } from '../api/employeeApi';
import toast from 'react-hot-toast';

const BLANK = { age:30, gender:'Male', department:'Sales', job_role:'Sales Executive', monthly_income:5000, performance_rating:3, overtime:false, work_life_balance:3, job_satisfaction:3, years_at_company:5, education:3, marital_status:'Single', distance_from_home:10, num_companies_worked:2, total_working_years:8, training_times_last_year:3, years_since_last_promotion:2, years_with_curr_manager:3 };

function RiskBadge({ score }) {
  const pct = Math.round(score * 100);
  const color = pct > 70 ? 'text-red-600 bg-red-50 border-red-200' : pct > 40 ? 'text-yellow-600 bg-yellow-50 border-yellow-200' : 'text-green-600 bg-green-50 border-green-200';
  return <span className={`inline-block px-3 py-1 rounded-full text-sm font-bold border ${color}`}>{pct}%</span>;
}

export default function PredictionPage() {
  const [tab, setTab]           = useState('single');
  const [form, setForm]         = useState(BLANK);
  const [result, setResult]     = useState(null);
  const [loading, setLoading]   = useState(false);
  const [batchFile, setBatch]   = useState(null);
  const [batchResults, setBatchR] = useState([]);
  const [batchLoading, setBL]   = useState(false);
  const [employees, setEmployees] = useState([]);
  const [empLoaded, setEL]      = useState(false);

  const loadEmployees = async () => {
    if (empLoaded) return;
    try {
      const data = await getAllEmployees(1, '', '', 100);
      setEmployees(data.employees ?? data);
      setEL(true);
    } catch {}
  };

  const selectEmployee = (e) => {
    const emp = employees.find(x => String(x.id) === e.target.value);
    if (emp) setForm({ ...BLANK, ...emp, overtime: !!emp.overtime });
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm(p => ({ ...p, [name]: type === 'checkbox' ? checked : value }));
  };

  const runPrediction = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const payload = { ...form, age: +form.age, monthly_income: +form.monthly_income, years_at_company: +form.years_at_company, distance_from_home: +form.distance_from_home, performance_rating: +form.performance_rating, work_life_balance: +form.work_life_balance, job_satisfaction: +form.job_satisfaction, education: +form.education, num_companies_worked: +form.num_companies_worked, total_working_years: +form.total_working_years, training_times_last_year: +form.training_times_last_year, years_since_last_promotion: +form.years_since_last_promotion, years_with_curr_manager: +form.years_with_curr_manager, overtime: form.overtime ? 'Yes' : 'No' };
      const data = await predictSingle(payload);
      setResult(data);
      toast.success('Prediction complete!');
    } catch (err) {
      let msg = 'Prediction failed';
      if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          msg = err.response.data.detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join(', ');
        } else if (typeof err.response.data.detail === 'string') {
          msg = err.response.data.detail;
        } else {
          msg = JSON.stringify(err.response.data.detail);
        }
      }
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const runBatch = async () => {
    if (!batchFile) return toast.error('Please select a CSV file');
    setBL(true);
    try {
      const data = await predictBatch(batchFile);
      setBatchR(data.results ?? data);
      toast.success(`Processed ${(data.results ?? data).length} employees`);
    } catch (err) {
      let msg = 'Batch failed';
      if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          msg = err.response.data.detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join(', ');
        } else if (typeof err.response.data.detail === 'string') {
          msg = err.response.data.detail;
        } else {
          msg = JSON.stringify(err.response.data.detail);
        }
      }
      toast.error(msg);
    } finally {
      setBL(false);
    }
  };

  return (
    <div className="space-y-5">
      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-200">
        {['single','batch'].map(t => (
          <button key={t} onClick={() => setTab(t)} className={`px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px ${tab===t ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700'}`}>
            {t === 'single' ? 'Single Prediction' : 'Batch Prediction'}
          </button>
        ))}
      </div>

      {tab === 'single' && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {/* Form */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
            <h2 className="font-semibold text-slate-800">Employee Data</h2>

            {/* Auto-fill from existing employee */}
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Auto-fill from existing employee</label>
              <select onClick={loadEmployees} onChange={selectEmployee} className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="">— Select employee —</option>
                {employees.map(e => <option key={e.id} value={e.id}>{e.first_name} {e.last_name}</option>)}
              </select>
            </div>

            <form onSubmit={runPrediction} className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <F label="Age" name="age" type="number" min="18" max="65" value={form.age} onChange={handleChange} />
                <S label="Gender" name="gender" value={form.gender} onChange={handleChange} opts={['Male','Female']} />
                <S label="Department" name="department" value={form.department} onChange={handleChange} opts={['Sales','Research & Development','Human Resources']} />
                <S label="Job Role" name="job_role" value={form.job_role} onChange={handleChange} opts={['Sales Executive','Research Scientist','Laboratory Technician','Manufacturing Director','Healthcare Representative','Manager','Sales Representative','Research Director','Human Resources']} />
                <F label="Monthly Income" name="monthly_income" type="number" value={form.monthly_income} onChange={handleChange} />
                <F label="Years at Company" name="years_at_company" type="number" value={form.years_at_company} onChange={handleChange} />
                <F label="Total Working Years" name="total_working_years" type="number" value={form.total_working_years} onChange={handleChange} />
                <F label="Distance from Home" name="distance_from_home" type="number" value={form.distance_from_home} onChange={handleChange} />
                <S label="Job Satisfaction (1-4)" name="job_satisfaction" value={form.job_satisfaction} onChange={handleChange} opts={[1,2,3,4]} />
                <S label="Work-Life Balance (1-4)" name="work_life_balance" value={form.work_life_balance} onChange={handleChange} opts={[1,2,3,4]} />
                <S label="Performance Rating (1-4)" name="performance_rating" value={form.performance_rating} onChange={handleChange} opts={[1,2,3,4]} />
                <S label="Education (1-5)" name="education" value={form.education} onChange={handleChange} opts={[1,2,3,4,5]} />
                <F label="Num Companies Worked" name="num_companies_worked" type="number" value={form.num_companies_worked} onChange={handleChange} />
                <F label="Yrs Since Last Promotion" name="years_since_last_promotion" type="number" value={form.years_since_last_promotion} onChange={handleChange} />
                <F label="Yrs With Curr Manager" name="years_with_curr_manager" type="number" value={form.years_with_curr_manager} onChange={handleChange} />
                <F label="Training Times Last Yr" name="training_times_last_year" type="number" value={form.training_times_last_year} onChange={handleChange} />
                <S label="Marital Status" name="marital_status" value={form.marital_status} onChange={handleChange} opts={['Single','Married','Divorced']} />
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" name="overtime" id="ot" checked={form.overtime} onChange={handleChange} className="w-4 h-4 text-blue-600" />
                <label htmlFor="ot" className="text-sm text-slate-700">Works Overtime</label>
              </div>
              <button type="submit" disabled={loading} className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-2.5 rounded-lg text-sm transition-colors flex items-center justify-center gap-2">
                {loading ? <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>Running...</> : 'Run Prediction'}
              </button>
            </form>
          </div>

          {/* Results */}
          <div className="space-y-4">
            {!result ? (
              <div className="bg-slate-50 rounded-xl border-2 border-dashed border-slate-300 p-10 text-center text-slate-400">
                <svg xmlns="http://www.w3.org/2000/svg" className="w-12 h-12 mx-auto mb-3 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
                <p className="font-medium">Fill in the form and click Run Prediction</p>
                <p className="text-sm mt-1">Results from all 3 models will appear here</p>
              </div>
            ) : (
              <>
                {/* Main risk score */}
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
                  <h3 className="font-semibold text-slate-700 mb-3">Overall Risk Score</h3>
                  <div className="flex items-center gap-4">
                    <div className={`text-5xl font-bold ${result.ensemble_risk_score > 0.7 ? 'text-red-600' : result.ensemble_risk_score > 0.4 ? 'text-yellow-600' : 'text-green-600'}`}>
                      {Math.round((result.ensemble_risk_score ?? 0) * 100)}%
                    </div>
                    <div>
                      <p className="font-semibold text-slate-800">{result.ensemble_prediction === 'Yes' ? 'At Risk of Leaving' : 'Likely to Stay'}</p>
                      <p className="text-xs text-slate-500 mt-0.5">Based on ensemble of 3 models</p>
                    </div>
                  </div>
                </div>

                {/* Per-model results */}
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
                  <h3 className="font-semibold text-slate-700 mb-3">Model Breakdown</h3>
                  <div className="space-y-2">
                    {(result.models ?? []).map((m, i) => (
                      <div key={i} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                        <span className="text-sm text-slate-700">{m.model_name}</span>
                        <div className="flex items-center gap-3">
                          <div className="w-24 bg-slate-200 rounded-full h-2">
                            <div className={`h-2 rounded-full ${m.risk_score > 0.7 ? 'bg-red-500' : m.risk_score > 0.4 ? 'bg-yellow-500' : 'bg-green-500'}`} style={{ width: `${Math.round(m.risk_score * 100)}%` }}></div>
                          </div>
                          <RiskBadge score={m.risk_score} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Key risk factors */}
                {result.key_factors?.length > 0 && (
                  <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
                    <h3 className="font-semibold text-slate-700 mb-3">Key Risk Factors</h3>
                    <ul className="space-y-1.5">
                      {result.key_factors.map((f, i) => (
                        <li key={i} className="flex items-center gap-2 text-sm text-slate-600">
                          <span className="w-1.5 h-1.5 bg-red-500 rounded-full flex-shrink-0"></span>{f}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* AI recommendation */}
                {result.recommendation && (
                  <div className="bg-blue-50 border border-blue-200 rounded-xl p-5">
                    <h3 className="font-semibold text-blue-800 mb-2">HR Recommendation</h3>
                    <p className="text-sm text-blue-700 leading-relaxed">{result.recommendation}</p>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {tab === 'batch' && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-5">
          <div>
            <h2 className="font-semibold text-slate-800 mb-1">Batch CSV Prediction</h2>
            <p className="text-sm text-slate-500">Upload a CSV file with employee data to predict attrition risk for multiple employees at once.</p>
          </div>

          <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-10 h-10 mx-auto mb-2 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
            <p className="text-sm text-slate-600 mb-3">Click to select a CSV file</p>
            <input type="file" accept=".csv" onChange={e => setBatch(e.target.files[0])} className="text-sm text-slate-600" />
            {batchFile && <p className="mt-2 text-xs text-green-600 font-medium">Selected: {batchFile.name}</p>}
          </div>

          <button onClick={runBatch} disabled={batchLoading || !batchFile} className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold rounded-lg text-sm transition-colors flex items-center gap-2">
            {batchLoading ? <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>Processing...</> : 'Run Batch Prediction'}
          </button>

          {batchResults.length > 0 && (
            <div className="overflow-x-auto rounded-lg border border-slate-200">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>{['Employee','Risk Score','Prediction','Recommendation'].map(h => <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">{h}</th>)}</tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {batchResults.map((r, i) => (
                    <tr key={i} className={`hover:bg-slate-50 ${r.attrition_prediction === 'Yes' ? 'bg-red-50/40' : ''}`}>
                      <td className="px-4 py-3 font-medium">{r.employee_name ?? `Employee ${i+1}`}</td>
                      <td className="px-4 py-3"><RiskBadge score={r.risk_score} /></td>
                      <td className="px-4 py-3"><span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${r.attrition_prediction === 'Yes' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>{r.attrition_prediction}</span></td>
                      <td className="px-4 py-3 text-slate-500 text-xs max-w-xs truncate">{r.recommendation ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Reusable form helpers (moved outside main component function to prevent focus loss)
const F = ({ label, name, type = 'text', value, onChange, ...rest }) => (
  <div>
    <label className="block text-xs font-medium text-slate-600 mb-1">{label}</label>
    <input
      name={name}
      type={type}
      value={value}
      onChange={onChange}
      className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      {...rest}
    />
  </div>
);

const S = ({ label, name, value, onChange, opts }) => (
  <div>
    <label className="block text-xs font-medium text-slate-600 mb-1">{label}</label>
    <select
      name={name}
      value={value}
      onChange={onChange}
      className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      {opts.map(o => (
        <option key={o} value={o}>{o}</option>
      ))}
    </select>
  </div>
);
