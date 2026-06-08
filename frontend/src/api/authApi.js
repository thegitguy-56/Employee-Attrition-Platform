// authApi.js — all authentication API calls
import apiClient from './client';

// Login: sends email+password, gets back token + user info
export const login = async (email, password) => {
  const response = await apiClient.post('/api/auth/login', { email, password });
  return response.data;
};

// Register: admin creates a new HR user
export const register = async (userData) => {
  const response = await apiClient.post('/api/auth/register', userData);
  return response.data;
};

// Get current logged-in user's profile
export const getCurrentUser = async () => {
  const response = await apiClient.get('/api/auth/me');
  return response.data;
};
