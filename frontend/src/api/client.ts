/**
 * API Client for FlirtDeck Backend
 * 
 * BIG PICTURE:
 * This file creates a configured Axios instance that handles ALL communication
 * with our backend API. Think of it as a specialized mailman who:
 * 1. Knows where to deliver (API_URL)
 * 2. Always includes your ID badge (auth token) with every delivery
 * 3. Handles errors consistently
 * 
 * WHY WE NEED THIS:
 * - Single source of truth for API URL
 * - Automatically adds auth token to every request (don't forget it!)
 * - Handles token expiration and redirects to login
 * - Consistent error handling across the app
 * 
 * ANALOGY:
 * Instead of writing this every time:
 *   fetch('https://api.../users', { headers: { Authorization: 'Bearer token' } })
 * 
 * We write:
 *   apiClient.get('/users')
 * 
 * And the client automatically adds the auth token!
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import type { ApiError } from '../types';

// ============================================
// CONFIGURATION
// ============================================

/**
 * Get API URL from environment variables
 * 
 * Vite exposes env vars as import.meta.env.VITE_*
 * We set these in .env.local
 * 
 * Falls back to localhost if not set (for local backend development)
 */
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

/**
 * Create the Axios instance
 * 
 * baseURL: All requests are relative to this (e.g., get('/users') → https://api.../users)
 * timeout: Cancel request if it takes longer than 30 seconds
 * headers: Default headers for all requests
 */
const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================================
// REQUEST INTERCEPTOR (Outgoing)
// ============================================

/**
 * Request Interceptor - Runs BEFORE every API request
 * 
 * BIG PICTURE:
 * This is like a security guard checking your badge before letting you in.
 * Every time you make an API call, this function:
 * 1. Checks localStorage for an auth token
 * 2. Adds it to the request headers
 * 3. Sends the request to the backend
 * 
 * WHY:
 * - API Gateway checks the Authorization header to validate you're logged in
 * - Without this, you'd get "401 Unauthorized" on every protected endpoint
 * 
 * FLOW:
 * Component calls: apiClient.get('/connections')
 *   ↓
 * Interceptor adds: headers['Authorization'] = 'Bearer your-token-here'
 *   ↓
 * Request sent to: https://api.../connections with auth header
 *   ↓
 * Backend validates token and returns data
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Get the ID token from localStorage
    // This was stored during login (see AuthContext.tsx)
    const token = localStorage.getItem('idToken');
    
    // If token exists, add it to the Authorization header
    // Format: "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
    // The backend expects this exact format
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Return the modified config so the request can proceed
    return config;
  },
  (error) => {
    // If something goes wrong in the interceptor itself, reject
    // This is rare (would mean localStorage is broken or similar)
    return Promise.reject(error);
  }
);

// ============================================
// RESPONSE INTERCEPTOR (Incoming)
// ============================================

/**
 * Response Interceptor - Runs AFTER every API response
 * 
 * BIG PICTURE:
 * This handles errors globally so we don't repeat error logic everywhere.
 * It's like a mail sorter that checks incoming mail and handles problems:
 * - If mail is good → pass it through
 * - If mail says "access denied" → redirect to login
 * - If mail is damaged → log it and show user-friendly error
 * 
 * HANDLES TWO CASES:
 * 1. Successful response (status 200-299) → pass through unchanged
 * 2. Error response (status 400+) → check what type of error and handle it
 * 
 * MOST IMPORTANT CASE: 401 Unauthorized
 * If backend returns 401, it means:
 * - Token expired (they last 1 hour)
 * - Token is invalid
 * - User needs to login again
 * 
 * So we automatically clear localStorage and redirect to login.
 */
apiClient.interceptors.response.use(
  // Success case: just return the response unchanged
  (response) => {
    return response;
  },
  
  // Error case: handle different error types
  (error: AxiosError<ApiError>) => {
    // 401 Unauthorized - Token expired or invalid
    if (error.response?.status === 401) {
      console.log('Authentication failed - redirecting to login');
      
      // Clear all auth data from localStorage
      // This is important - don't keep invalid tokens around
      localStorage.removeItem('idToken');
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      
      // Redirect to login page
      // This forces the user to re-authenticate with Google
      window.location.href = '/login';
    }
    
    // 403 Forbidden - User doesn't have permission
    // Example: Free user trying to create 2nd connection
    if (error.response?.status === 403) {
      console.log('Access forbidden:', error.response.data);
      // Could show a "Upgrade to Premium" modal here
      // For now, just let the error bubble up to the component
    }
    
    // 500 Internal Server Error - Backend is broken
    if (error.response?.status === 500) {
      console.error('Server error:', error.response.data);
      // Could show a "Something went wrong, try again later" message
    }
    
    // Network error - User is offline or API is unreachable
    if (!error.response) {
      console.error('Network error - check your connection');
    }
    
    // Return the error so the calling code can handle it
    // This allows components to do custom error handling if needed
    return Promise.reject(error);
  }
);

// ============================================
// HELPER FUNCTIONS (Optional)
// ============================================

/**
 * Check if user is authenticated
 * 
 * Simple helper to check if tokens exist in localStorage
 * Used by components to decide whether to show login or dashboard
 */
export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem('idToken');
};

/**
 * Get current auth tokens
 * 
 * Returns all three tokens if they exist, null otherwise
 */
export const getAuthTokens = () => {
  const idToken = localStorage.getItem('idToken');
  const accessToken = localStorage.getItem('accessToken');
  const refreshToken = localStorage.getItem('refreshToken');
  
  if (!idToken || !accessToken || !refreshToken) {
    return null;
  }
  
  return { idToken, accessToken, refreshToken };
};

/**
 * Clear all authentication data
 * 
 * Used during logout or when tokens become invalid
 */
export const clearAuth = (): void => {
  localStorage.removeItem('idToken');
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('user'); // Also clear cached user data if we store it
};

// ============================================
// EXPORT
// ============================================

/**
 * Export the configured axios instance
 * 
 * Other files will import this and use it like:
 * 
 * import apiClient from '@/api/client';
 * 
 * const response = await apiClient.get('/auth/me');
 * const connections = await apiClient.get('/connections');
 * await apiClient.post('/connections', { name: 'Sarah' });
 * 
 * All of these will automatically include the auth token!
 */
export default apiClient;