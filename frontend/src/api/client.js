// client.js — the "phone line" between React and FastAPI
// Every API call in the app goes through this single Axios instance.
// This means we set up JWT tokens and error handling ONCE here,
// instead of repeating the same code in every file.

import axios from 'axios';

// Create an Axios instance with the backend base URL from .env
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: { 'Content-Type': 'application/json' },
});

// REQUEST INTERCEPTOR — runs before every API call goes out
// It reads the JWT token from localStorage and attaches it to the request header.
// This is how the backend knows who you are.
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// RESPONSE INTERCEPTOR — runs after every API response comes back
// If the backend returns 401 (Unauthorized), it means the token expired.
// We clear localStorage and send the user back to the login page.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
