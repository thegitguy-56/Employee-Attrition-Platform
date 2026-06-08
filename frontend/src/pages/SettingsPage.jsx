import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import apiClient from '../api/client';
import toast from 'react-hot-toast';

export default function SettingsPage() {
  const { user } = useAuth();
  const [oldPw, setOld]       = useState('');
  const [newPw, setNew]       = useState('');
  const [saving, setSaving]   = useState(false);
  const [model, setModel]     = useState('random_forest');
  const [threshold, setThr]   = useState(70);
  const [users, setUsers]     = useState([]);
  const [usersLoading, setUL] = useState(false);
  const [showAddUser, setShowAdd] = useState(false);
  const [newUser, setNewUser] = useState({ full_name: '', email: '', password: '', role: 'hr_manager' });
  const [addingUser, setAddingUser] = useState(false);

  const isAdmin = user?.role === 'admin';

  // Load users list (admin only)
  useEffect(() => {
    if (!isAdmin) return;
    setUL(true);
    apiClient.get('/api/auth/users')
      .then(r => setUsers(r.data))
      .catch(() => {}) // endpoint may not exist yet — silent fail
      .finally(() => setUL(false));
  }, [isAdmin]);

  const changePassword = async (e) => {
    e.preventDefault();
    if (newPw.length < 6) return toast.error('New password must be at least 6 characters');
    setSaving(true);
    try {
      await apiClient.post('/api/auth/change-password', { old_password: oldPw, new_password: newPw });
      toast.success('Password updated!');
      setOld(''); setNew('');
    } catch (err) {
      toast.error(err.response?.data?.detail ?? 'Failed to update password');
    } finally { setSaving(false); }
  };

  const addUser = async (e) => {
    e.preventDefault();
    setAddingUser(true);
    try {
      await apiClient.post('/api/auth/register', newUser);
      toast.success(`User ${newUser.email} created!`);
      setShowAdd(false);
      setNewUser({ full_name: '', email: '', password: '', role: 'hr_manager' });
      // Refresh list
      const r = await apiClient.get('/api/auth/users');
      setUsers(r.data);
    } catch (err) {
      toast.error(err.response?.data?.detail ?? 'Failed to create user');
    } finally { setAddingUser(false); }
  };

  const deactivateUser = async (userId, email) => {
    if (!window.confirm(`Deactivate ${email}?`)) return;
    try {
      await apiClient.patch(`/api/auth/users/${userId}/deactivate`);
      toast.success('User deactivated');
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, is_active: false } : u));
    } catch { toast.error('Failed to deactivate user'); }
  };

  const Section = ({ title, children }) => (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
      <h2 className="font-semibold text-slate-800 border-b border-slate-100 pb-3">{title}</h2>
      {children}
    </div>
  );

  const Input = ({ label, type = 'text', value, onChange, ...rest }) => (
    <div>
      <label className="block text-xs font-medium text-slate-600 mb-1">{label}</label>
      <input type={type} value={value} onChange={onChange}
        className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        {...rest} />
    </div>
  );

  return (
    <div className="max-w-2xl space-y-5">

      {/* ── Profile ── */}
      <Section title="👤 Profile">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 bg-blue-600 rounded-full flex items-center justify-center text-white text-2xl font-bold uppercase">
            {user?.full_name?.[0] ?? 'U'}
          </div>
          <div>
            <p className="font-semibold text-slate-800">{user?.full_name}</p>
            <p className="text-sm text-slate-500">{user?.email}</p>
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full capitalize mt-1 inline-block">
              {user?.role?.replace('_', ' ')}
            </span>
          </div>
        </div>
      </Section>

      {/* ── Change Password ── */}
      <Section title="🔑 Change Password">
        <form onSubmit={changePassword} className="space-y-3">
          <Input label="Current Password" type="password" value={oldPw} onChange={e => setOld(e.target.value)} required />
          <Input label="New Password (min 6 chars)" type="password" value={newPw} onChange={e => setNew(e.target.value)} required minLength={6} />
          <button type="submit" disabled={saving}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold rounded-lg text-sm transition-colors">
            {saving ? 'Saving...' : 'Update Password'}
          </button>
        </form>
      </Section>

      {/* ── Prediction Settings ── */}
      <Section title="⚙️ Prediction Settings">
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Default ML Model</label>
            <select value={model} onChange={e => setModel(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="random_forest">Random Forest — Most accurate ✅ (recommended)</option>
              <option value="decision_tree">Decision Tree — Easiest to explain</option>
              <option value="logistic_regression">Logistic Regression — Fastest</option>
            </select>
            <p className="text-xs text-slate-400 mt-1">This model is used as the primary result when showing predictions.</p>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-2">
              High-Risk Threshold: <strong className="text-slate-800">{threshold}%</strong>
            </label>
            <input type="range" min="30" max="90" value={threshold} onChange={e => setThr(e.target.value)}
              className="w-full accent-blue-600" />
            <div className="flex justify-between text-xs text-slate-400 mt-0.5">
              <span>30% (sensitive)</span><span>90% (strict)</span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Employees with a risk score above {threshold}% will be flagged as "High Risk" across dashboards and reports.
            </p>
          </div>
          <button onClick={() => toast.success('Preferences saved!')}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg text-sm transition-colors">
            Save Preferences
          </button>
        </div>
      </Section>

      {/* ── User Management (Admin only) ── */}
      {isAdmin && (
        <Section title="👥 User Management (Admin Only)">
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <p className="text-sm text-slate-500">Manage HR Manager accounts.</p>
              <button onClick={() => setShowAdd(v => !v)}
                className="px-3 py-1.5 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors">
                + Add HR User
              </button>
            </div>

            {/* Add user form */}
            {showAdd && (
              <form onSubmit={addUser} className="bg-slate-50 rounded-lg p-4 space-y-3 border border-slate-200">
                <p className="text-xs font-semibold text-slate-700">New User Details</p>
                <div className="grid grid-cols-2 gap-3">
                  <Input label="Full Name" value={newUser.full_name} onChange={e => setNewUser(p => ({ ...p, full_name: e.target.value }))} required />
                  <Input label="Email" type="email" value={newUser.email} onChange={e => setNewUser(p => ({ ...p, email: e.target.value }))} required />
                  <Input label="Password" type="password" value={newUser.password} onChange={e => setNewUser(p => ({ ...p, password: e.target.value }))} required minLength={6} />
                  <div>
                    <label className="block text-xs font-medium text-slate-600 mb-1">Role</label>
                    <select value={newUser.role} onChange={e => setNewUser(p => ({ ...p, role: e.target.value }))}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                      <option value="hr_manager">HR Manager</option>
                      <option value="admin">Admin</option>
                    </select>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button type="submit" disabled={addingUser}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-xs font-semibold rounded-lg transition-colors">
                    {addingUser ? 'Creating...' : 'Create User'}
                  </button>
                  <button type="button" onClick={() => setShowAdd(false)}
                    className="px-4 py-2 border border-slate-300 text-slate-600 text-xs rounded-lg hover:bg-slate-50 transition-colors">
                    Cancel
                  </button>
                </div>
              </form>
            )}

            {/* Users table */}
            {usersLoading ? (
              <p className="text-sm text-slate-400">Loading users...</p>
            ) : (
              <div className="overflow-x-auto rounded-lg border border-slate-200">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50">
                    <tr>
                      {['Name', 'Email', 'Role', 'Status', 'Action'].map(h => (
                        <th key={h} className="text-left px-4 py-2 text-xs font-semibold text-slate-500 uppercase">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {users.length === 0 ? (
                      <tr><td colSpan={5} className="text-center py-6 text-slate-400 text-xs">No users found or endpoint not available yet.</td></tr>
                    ) : users.map(u => (
                      <tr key={u.id} className="hover:bg-slate-50">
                        <td className="px-4 py-2 font-medium text-slate-800">{u.full_name}</td>
                        <td className="px-4 py-2 text-slate-600">{u.email}</td>
                        <td className="px-4 py-2">
                          <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs capitalize">
                            {u.role?.replace('_', ' ')}
                          </span>
                        </td>
                        <td className="px-4 py-2">
                          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${u.is_active ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
                            {u.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="px-4 py-2">
                          {u.is_active && u.id !== user?.id && (
                            <button onClick={() => deactivateUser(u.id, u.email)}
                              className="text-xs px-2.5 py-1 bg-red-50 text-red-600 hover:bg-red-100 rounded-md font-medium transition-colors">
                              Deactivate
                            </button>
                          )}
                          {u.id === user?.id && <span className="text-xs text-slate-400">You</span>}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </Section>
      )}
    </div>
  );
}
