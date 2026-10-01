import client from './client';

export const auth = {
  login: (data) => client.post('/api/auth/login', data),
  signup: (data) => client.post('/api/auth/signup', data),
  getProfile: () => client.get('/api/auth/profile'),
};

export const analysis = {
  analyzeSingle: (data) => client.post('/api/analyze', data),
  analyzeBulk: (formData) => client.post('/api/analyze/bulk', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
};

export const history = {
  getHistory: (params) => client.get('/api/history', { params }),
  deleteOne: (id) => client.delete(`/api/history/${id}`),
  deleteAll: () => client.delete('/api/history'),
  exportCsv: () => client.get('/api/history/export', { responseType: 'blob' }),
};

export const dashboard = {
  getDashboard: () => client.get('/api/dashboard'),
};
