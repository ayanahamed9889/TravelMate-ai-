import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

// Attach token if it exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

const PUBLIC_PATHS = ['/', '/login', '/register'];

// Expired/invalid session -> log out. Login/register failures must NOT trigger this,
// otherwise a wrong password reloads the page and the error message is lost.
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const url = err.config?.url || '';
    const isAuthForm = url.includes('/auth/login') || url.includes('/auth/register');
    if (err.response?.status === 401 && !isAuthForm && localStorage.getItem('token')) {
      localStorage.removeItem('token');
      if (!PUBLIC_PATHS.includes(window.location.pathname)) window.location.assign('/login');
    }
    return Promise.reject(err);
  }
);

export default api;
