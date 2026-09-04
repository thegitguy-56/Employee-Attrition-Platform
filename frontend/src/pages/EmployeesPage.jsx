import { useState, useEffect, useCallback } from 'react';
import { getAllEmployees, deleteEmployee } from '../api/employeeApi';
import EmployeeForm from '../components/EmployeeForm';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import toast from 'react-hot-toast';

export default function EmployeesPage() {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState('');
  const [search, setSearch]       = useState('');
  const [department, setDept]     = useState('');
  const [page, setPage]           = useState(1);
  const [total, setTotal]         = useState(0);
  const [showForm, setShowForm]   = useState(false);
  const [editEmp, setEditEmp]     = useState(null);

  const DEPTS = ['', 'Sales', 'Research & Development', 'Human Resources'];
  const PER_PAGE = 10;

  const fetchEmployees = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getAllEmployees(page, search, department);
      setEmployees(data.employees ?? data);
      setTotal(data.total ?? data.length);
    } catch { setError('Failed to load employees.'); }
    finally { setLoading(false); }
  }, [page, search, department]);

  useEffect(() => { fetchEmployees(); }, [fetchEmployees]);

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Delete ${name}? This cannot be undone.`)) return;
    try {
      await deleteEmployee(id);
      toast.success('Employee deleted.');
      fetchEmployees();
    } catch { toast.error('Delete failed.'); }
  };

  const openEdit = (emp) => { setEditEmp(emp); setShowForm(true); };
  const openAdd  = ()    => { setEditEmp(null); setShowForm(true); };
  const closeForm = ()   => { setShowForm(false); setEditEmp(null); };

  const totalPages = Math.ceil(total / PER_PAGE);

  return (
    <div className="space-y-5">
      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <input
          type="text"
          placeholder="Search by name..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          className="flex-1 px-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <select
          value={department}
          onChange={(e) => { setDept(e.target.value); setPage(1); }}
          className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {DEPTS.map((d) => <option key={d} value={d}>{d || 'All Departments'}</option>)}
        </select>
        <button
          onClick={openAdd}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg transition-colors whitespace-nowrap"
        >
          + Add Employee
        </button>
      </div>

      {error && <ErrorMessage message={error} />}

      {/* Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          {loading ? <LoadingSpinner /> : (
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  {['Name','Department','Job Role','Income','Overtime','Satisfaction','Actions'].map(h => (
                    <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {employees.length === 0 ? (
                  <tr><td colSpan={7} className="text-center py-12 text-slate-400">No employees found.</td></tr>
                ) : employees.map((emp) => (
                  <tr key={emp.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 font-medium text-slate-800">{emp.first_name} {emp.last_name}</td>
                    <td className="px-4 py-3 text-slate-600">{emp.department}</td>
                    <td className="px-4 py-3 text-slate-600 max-w-[140px] truncate">{emp.job_role}</td>
                    <td className="px-4 py-3 text-slate-600">${emp.monthly_income?.toLocaleString()}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${emp.overtime ? 'bg-orange-100 text-orange-700' : 'bg-slate-100 text-slate-600'}`}>
                        {emp.overtime ? 'Yes' : 'No'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-600">{emp.job_satisfaction}/4</td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <button onClick={() => openEdit(emp)} className="text-xs px-2.5 py-1 bg-blue-50 text-blue-600 hover:bg-blue-100 rounded-md font-medium transition-colors">Edit</button>
                        <button onClick={() => handleDelete(emp.id, `${emp.first_name} ${emp.last_name}`)} className="text-xs px-2.5 py-1 bg-red-50 text-red-600 hover:bg-red-100 rounded-md font-medium transition-colors">Delete</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-slate-200">
            <p className="text-xs text-slate-500">Page {page} of {totalPages} · {total} employees</p>
            <div className="flex gap-2">
              <button disabled={page === 1} onClick={() => setPage(p => p - 1)} className="px-3 py-1 text-xs border border-slate-300 rounded-md hover:bg-slate-50 disabled:opacity-40">← Prev</button>
              <button disabled={page === totalPages} onClick={() => setPage(p => p + 1)} className="px-3 py-1 text-xs border border-slate-300 rounded-md hover:bg-slate-50 disabled:opacity-40">Next →</button>
            </div>
          </div>
        )}
      </div>

      {/* Modal */}
      {showForm && <EmployeeForm employee={editEmp} onClose={closeForm} onSaved={fetchEmployees} />}
    </div>
  );
}
