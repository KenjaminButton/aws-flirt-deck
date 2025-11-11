import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import apiClient, { clearAuth } from '../api/client';
import type { User } from '../types';

// Define the context type inline
interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: () => void;
  logout: () => void;
  isAuthenticated: boolean;
  refreshUser: () => Promise<void>;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider component
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  
  // Authentication initialization function
  const initAuth = async () => {
    const token = localStorage.getItem('idToken');
    
    if (!token) {
      setLoading(false);
      setUser(null);
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await apiClient.get<User>('/auth/me');
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      clearAuth();
      setUser(null);
    } finally {
      setLoading(false);
    }
  };
  
  // Run on mount
  useEffect(() => {
    initAuth();
  }, []);
  
  // Login function
  const login = () => {
    const cognitoDomain = import.meta.env.VITE_COGNITO_DOMAIN;
    const clientId = import.meta.env.VITE_COGNITO_CLIENT_ID;
    const redirectUri = import.meta.env.VITE_REDIRECT_URI;
    
    const oauthUrl = `https://${cognitoDomain}/oauth2/authorize?` +
      `response_type=code&` +
      `client_id=${clientId}&` +
      `redirect_uri=${encodeURIComponent(redirectUri)}&` +
      `identity_provider=Google&` +
      `scope=openid+email+profile`;
    
    window.location.href = oauthUrl;
  };
  
  // Logout function
  const logout = () => {
    clearAuth();
    setUser(null);
    window.location.href = '/login';
  };
  
  const isAuthenticated = user !== null;
  
  const value: AuthContextType = {
    user,
    loading,
    login,
    logout,
    isAuthenticated,
    refreshUser: initAuth
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};
