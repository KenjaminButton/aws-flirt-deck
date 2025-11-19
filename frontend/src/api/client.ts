import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    // Skip token check for the token exchange endpoint
    if (config.url?.includes('/auth/token')) {
      return config;
    }
    
    const token = localStorage.getItem('idToken');
    
    if (!token) {
      console.log('No token found - redirecting to login');
      localStorage.clear();
      window.location.href = '/login';
      return Promise.reject(new Error('No authentication token'));
    }
    
    config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);


export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem('idToken');
};


export const getAuthTokens = () => {
  const idToken = localStorage.getItem('idToken');
  const accessToken = localStorage.getItem('accessToken');
  const refreshToken = localStorage.getItem('refreshToken');
  
  if (!idToken || !accessToken || !refreshToken) {
    return null;
  }
  
  return { idToken, accessToken, refreshToken };
};

export const clearAuth = (): void => {
  localStorage.removeItem('idToken');
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('user'); 
};

export default apiClient;
