// EmployeeForm.jsx — modal form for creating OR editing an employee
// Props:
//   employee — if passed, the form pre-fills (edit mode); null = create mode
//   onClose  — function to close the modal
//   onSaved  — function called after successful save (refreshes the list)

import { useState } from 'react';
import { createEmployee, updateEmployee } from '../api/employeeApi';
import toast from 'react-hot-toast';

// All the options for dropdown fields
const DEPARTMENTS  = ['Sales', 'Research & Development', 'Human Resources'];
const JOB_ROLES    = ['Sales Executive', 'Research Scientist', 'Laboratory Technician', 'Manufacturing Director', 'Healthcare Representative', 'Manager', 'Sales Representative', 'Research Director', 'Human Resources'];
const EDUCATION    = [1, 2, 3, 4, 5]; // 1=Below College ... 5=Doctor
const MARITAL      = ['Single', 'Married', 'Divorced'];

// Default blank form values
const BLANK = {
  employee_number: '',
  first_name: '',
  last_name: '',
  age: '',
  gender: 'Male',
  department: 'Sales',
  job_role: 'Sales Executive',
  monthly_income: '',
  performance_rating: 3,
  overtime: false,
  work_life_balance: 3,
  job_satisfaction: 3,
  years_at_company: '',
  education: 3,
  marital_status: 'Single',
  distance_from_home: '',
};

// Reusable input wrapper (moved outside components to prevent focus loss)
const Field = ({ label, name, value, onChange, type = 'text', ...rest }) => (
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

const Select = ({ label, name, value, onChange, options }) => (
  <div>
    <label className="block text-xs font-medium text-slate-600 mb-1">{label}</label>
    <select
      name={name}
      value={value}
      onChange={onChange}
      className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      {options.map((o) => (
        <option key={o} value={o}>{o}</option>
      ))}
    </select>
  </div>
);

export default function EmployeeForm({ employee = null, onClose, onSaved }) {
  // If editing, pre-fill form with existing data and parse overtime string to boolean
  const [form, setForm]     = useState(
    employee 
      ? { ...employee, overtime: employee.overtime === 'Yes' } 
      : BLANK
  );
  const [loading, setLoading] = useState(false);

  const isEdit = !!employee;

  // Generic input change handler — updates any field by name
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Convert number strings to actual numbers and boolean overtime to 'Yes'/'No'
      const payload = {
        ...form,
        age:               Number(form.age),
        monthly_income:    Number(form.monthly_income),
        years_at_company:  Number(form.years_at_company),
        distance_from_home: Number(form.distance_from_home),
        performance_rating: Number(form.performance_rating),
        work_life_balance:  Number(form.work_life_balance),
        job_satisfaction:   Number(form.job_satisfaction),
        education:          Number(form.education),
        overtime:           form.overtime ? 'Yes' : 'No',
      };

      if (isEdit) {
        await updateEmployee(employee.id, payload);
        toast.success('Employee updated successfully!');
      } else {
        await createEmployee(payload);
        toast.success('Employee added successfully!');
      }
      onSaved(); // Tell parent to refresh the list
      onClose(); // Close the modal
    } catch (err) {
      let msg = 'Failed to save employee';
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

  return (
    // Modal backdrop
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Modal header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 sticky top-0 bg-white">
          <h2 className="font-bold text-slate-800">{isEdit ? 'Edit Employee' : 'Add New Employee'}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-xl">✕</button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Field label="Employee Number" name="employee_number" value={form.employee_number} onChange={handleChange} required />
            <Field label="First Name" name="first_name" value={form.first_name} onChange={handleChange} required />
            <Field label="Last Name" name="last_name" value={form.last_name} onChange={handleChange} required />
            <Field label="Age" name="age" type="number" min="18" max="65" value={form.age} onChange={handleChange} required />
            <Select label="Gender" name="gender" value={form.gender} onChange={handleChange} options={['Male', 'Female']} />
            <Select label="Department" name="department" value={form.department} onChange={handleChange} options={DEPARTMENTS} />
            <Select label="Job Role" name="job_role" value={form.job_role} onChange={handleChange} options={JOB_ROLES} />
            <Field label="Monthly Income ($)" name="monthly_income" type="number" min="0" value={form.monthly_income} onChange={handleChange} required />
            <Select label="Marital Status" name="marital_status" value={form.marital_status} onChange={handleChange} options={MARITAL} />
            <Select label="Education (1–5)" name="education" value={form.education} onChange={handleChange} options={EDUCATION} />
            <Field label="Years at Company" name="years_at_company" type="number" min="0" value={form.years_at_company} onChange={handleChange} required />
            <Field label="Distance from Home (km)" name="distance_from_home" type="number" min="0" value={form.distance_from_home} onChange={handleChange} required />
            <Select label="Performance Rating (1–4)" name="performance_rating" value={form.performance_rating} onChange={handleChange} options={[1,2,3,4]} />
            <Select label="Work-Life Balance (1–4)" name="work_life_balance" value={form.work_life_balance} onChange={handleChange} options={[1,2,3,4]} />
            <Select label="Job Satisfaction (1–4)" name="job_satisfaction" value={form.job_satisfaction} onChange={handleChange} options={[1,2,3,4]} />
          </div>

          {/* Overtime checkbox */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              name="overtime"
              id="overtime"
              checked={form.overtime}
              onChange={handleChange}
              className="w-4 h-4 text-blue-600"
            />
            <label htmlFor="overtime" className="text-sm text-slate-700 font-medium">
              Works Overtime
            </label>
          </div>

          {/* Submit buttons */}
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm text-slate-600 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 text-sm bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold rounded-lg transition-colors flex items-center gap-2"
            >
              {loading ? (
                <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>Saving...</>
              ) : (
                isEdit ? 'Save Changes' : 'Add Employee'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
