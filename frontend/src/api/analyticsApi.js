// analyticsApi.js — analytics endpoints
import apiClient from './client';

export const getOverview = async () => {
  const response = await apiClient.get('/api/analytics/overview');
  return response.data;
};

export const getByDepartment = async () => {
  const response = await apiClient.get('/api/analytics/by-department');
  return response.data;
};

export const getBySatisfaction = async () => {
  const response = await apiClient.get('/api/analytics/by-satisfaction');
  return response.data;
};

export const getSalaryAnalysis = async () => {
  const response = await apiClient.get('/api/analytics/salary-analysis');
  return response.data;
};

export const getTopRisk = async () => {
  const response = await apiClient.get('/api/analytics/top-risk');
  return response.data;
};

export const getFeatureImportance = async () => {
  const response = await apiClient.get('/api/analytics/feature-importance');
  return response.data;
};
