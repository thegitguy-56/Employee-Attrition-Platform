// predictionApi.js — prediction endpoints
import apiClient from './client';

export const predictSingle = async (employeeData) => {
  const response = await apiClient.post('/api/predict/single', employeeData);
  return response.data;
};

export const predictBatch = async (csvFile) => {
  const formData = new FormData();
  formData.append('file', csvFile);
  const response = await apiClient.post('/api/predict/batch', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const getPredictionHistory = async () => {
  const response = await apiClient.get('/api/predict/history');
  return response.data;
};
