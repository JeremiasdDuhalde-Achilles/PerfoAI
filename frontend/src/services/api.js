import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle 401 errors
api.interceptors.response.use(
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

// Auth API
export const authAPI = {
  login: (username, password) =>
    api.post('/api/v1/auth/login', { username, password }),

  register: (userData) =>
    api.post('/api/v1/auth/register', userData),

  getCurrentUser: () =>
    api.get('/api/v1/auth/me'),
};

// Invoices API
export const invoicesAPI = {
  list: (params) =>
    api.get('/api/v1/invoices/', { params }),

  get: (id) =>
    api.get(`/api/v1/invoices/${id}`),

  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/v1/invoices/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  update: (id, data) =>
    api.put(`/api/v1/invoices/${id}`, data),

  approve: (id) =>
    api.post(`/api/v1/invoices/${id}/approve`),

  reject: (id, reason) =>
    api.post(`/api/v1/invoices/${id}/reject`, null, { params: { reason } }),

  getStats: () =>
    api.get('/api/v1/invoices/stats/overview'),

  getDashboardMetrics: () =>
    api.get('/api/v1/invoices/dashboard/metrics'),
};

// Suppliers API
export const suppliersAPI = {
  list: (params) =>
    api.get('/api/v1/suppliers/', { params }),

  get: (id) =>
    api.get(`/api/v1/suppliers/${id}`),

  create: (data) =>
    api.post('/api/v1/suppliers/', data),

  update: (id, data) =>
    api.put(`/api/v1/suppliers/${id}`, data),

  delete: (id) =>
    api.delete(`/api/v1/suppliers/${id}`),
};

export default api;
