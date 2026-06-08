// employeeApi.js — all employee CRUD API calls
import apiClient from './client';

export const getAllEmployees = async (page = 1, search = '', department = '') => {
  const response = await apiClient.get('/api/employees', {
    params: { page, search, department, limit: 10 },
  });
  return response.data;
};

export const getEmployee = async (id) => {
  const response = await apiClient.get(`/api/employees/${id}`);
  return response.data;
};

export const createEmployee = async (data) => {
  const response = await apiClient.post('/api/employees', data);
  return response.data;
};

export const updateEmployee = async (id, data) => {
  const response = await apiClient.put(`/api/employees/${id}`, data);
  return response.data;
};

export const deleteEmployee = async (id) => {
  const response = await apiClient.delete(`/api/employees/${id}`);
  return response.data;
};

export const searchEmployees = async (query) => {
  const response = await apiClient.get('/api/employees/search', { params: { query } });
  return response.data;
};
