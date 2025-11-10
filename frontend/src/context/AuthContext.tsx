/**
 * Authentication Context for FlirtDeck
 * 
 * BIG PICTURE:
 * This file creates a React Context that manages authentication state across
 * the entire application. Think of it as a "global auth manager" that:
 * 
 * 1. Checks if user is logged in when app loads
 * 2. Fetches user profile from backend
 * 3. Provides login/logout functions to any component
 * 4. Makes user data available everywhere (no prop drilling!)
 * 
 * WHY WE NEED THIS:
 * Without Context, we'd have to pass user data through every component:
 *   App → Dashboard → Sidebar → UserProfile (passing 'user' prop 4 levels!)
 * 
 * With Context, any component can access user data directly:
 *   const { user } = useAuth(); // Works anywhere!
 * 
 * ANALOGY:
 * Context is like a company-wide announcement system.
 * Instead of telling each person individually "John is the CEO",
 * you announce it once and everyone can look it up when they need it.
 * 
 * REACT CONTEXT PATTERN:
 * 1. Create a Context (createContext)
 * 2. Create a Provider component (AuthProvider)
 * 3. Wrap your app with the Provider
 * 4. Use the hook (useAuth) in any component to access the data
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import apiClient, { clearAuth } from '../api/client';
import type { User, AuthContextType } from '../types';

// ============================================
// 1. CREATE THE CONTEXT
// ============================================

/**
 * Create the Auth Context
 * 
 * This is like creating an empty box that will hold our auth state.
 * We initialize it as 'undefined' because we'll fill it in the Provider.
 * 
 * The '!' tells TypeScript "trust me, this will be defined when used"
 * (because we'll throw an error if someone tries to use it outside Provider)
 */
const AuthContext = createContext<AuthContextType>(undefined!);

// ============================================
// 2. CREATE THE PROVIDER COMPONENT
// ============================================

/**
 * AuthProvider Component
 * 
 * BIG PICTURE:
 * This component wraps your entire app and provides auth state to all children.
 * It manages three pieces of state:
 * - user: Current logged-in user (null if not logged in)
 * - loading: True while checking authentication (prevents flash of wrong UI)
 * - Auth functions: login() and logout()
 * 
 * LIFECYCLE:
 * 1. Component mounts → useEffect runs
 * 2. Check localStorage for token
 * 3. If token exists, fetch user profile from /auth/me
 * 4. Set user state with profile data
 * 5. Components can now access user via useAuth()
 * 
 * Props:
 * - children: The rest of your app (wrapped by this provider)
 */
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // State: Current user (null = not logged in, User object = logged in)
  const [user, setUser] = useState<User | null>(null);
  
  // State: Loading flag (prevents flash of login page while checking auth)
  const [loading, setLoading] = useState<boolean>(true);
  
  // ============================================
  // INITIALIZATION: Check if user is already logged in
  // ============================================
  
  /**
   * useEffect - Runs once when component mounts
   * 
   * This checks if there's an existing session:
   * 1. Look for token in localStorage
   * 2. If found, fetch user profile
   * 3. Set user state
   * 4. Stop loading
   * 
   * WHY:
   * When user refreshes the page, we need to restore their session.
   * Without this, they'd be logged out every time they refresh!
   */
  useEffect(() => {
    const initAuth = async () => {
      // Check if we have an ID token in localStorage
      const token = localStorage.getItem('idToken');
      
      if (!token) {
        // No token = not logged in
        setLoading(false);
        return;
      }
      
      // Token exists! Try to fetch user profile
      try {
        // Call our backend GET /auth/me endpoint
        // This validates the token and returns user data
        const response = await apiClient.get<User>('/auth/me');
        
        // Success! Set the user state
        setUser(response.data);
      } catch (error) {
        // Token is invalid or expired
        console.error('Failed to fetch user profile:', error);
        
        // Clear the invalid token
        clearAuth();
        
        // User will see login page
      } finally {
        // Always stop loading, whether success or failure
        setLoading(false);
      }
    };
    
    // Run the initialization
    initAuth();
  }, []); // Empty dependency array = run once on mount
  
  // ============================================
  // LOGIN FUNCTION
  // ============================================
  
  /**
   * login() - Redirect user to Google OAuth
   * 
   * BIG PICTURE:
   * This constructs the Cognito Hosted UI URL and redirects the user.
   * The flow is:
   * 1. User clicks "Sign in with Google"
   * 2. We call login()
   * 3. Browser redirects to Cognito
   * 4. Cognito redirects to Google
   * 5. User approves on Google
   * 6. Google redirects back to Cognito
   * 7. Cognito redirects to our callback URL with a code
   * 8. Callback page exchanges code for tokens (Day 9)
   * 
   * URL PARAMETERS EXPLAINED:
   * - response_type=code: Use authorization code flow (most secure)
   * - client_id: Identifies our app to Cognito
   * - redirect_uri: Where to send user after login
   * - identity_provider=Google: Skip Cognito login, go straight to Google
   * - scope: What data we want (openid=user ID, email, profile=name/picture)
   */
  const login = () => {
    // Get config from environment variables
    const cognitoDomain = import.meta.env.VITE_COGNITO_DOMAIN;
    const clientId = import.meta.env.VITE_COGNITO_CLIENT_ID;
    const redirectUri = import.meta.env.VITE_REDIRECT_URI;
    
    // Construct the OAuth URL
    // This is the standard OAuth 2.0 authorization code flow URL
    const oauthUrl = `https://${cognitoDomain}/oauth2/authorize?` +
      `response_type=code&` +
      `client_id=${clientId}&` +
      `redirect_uri=${encodeURIComponent(redirectUri)}&` +
      `identity_provider=Google&` +
      `scope=openid+email+profile`;
    
    // Redirect the browser to Cognito/Google
    window.location.href = oauthUrl;
  };
  
  // ============================================
  // LOGOUT FUNCTION
  // ============================================
  
  /**
   * logout() - Clear session and redirect to login
   * 
   * BIG PICTURE:
   * This logs the user out by:
   * 1. Clearing tokens from localStorage
   * 2. Clearing user state
   * 3. Redirecting to login page
   * 
   * NOTE: This is a "local logout" - we clear our session but don't tell Cognito.
   * For production, you might want to call Cognito's logout endpoint too.
   * 
   * FLOW:
   * User clicks "Logout" button
   *   ↓
   * Component calls logout()
   *   ↓
   * Clear localStorage and state
   *   ↓
   * Redirect to /login
   *   ↓
   * User sees login page
   */
  const logout = () => {
    // Clear all auth data from localStorage
    clearAuth();
    
    // Clear user state (triggers re-render of components)
    setUser(null);
    
    // Redirect to login page
    window.location.href = '/login';
  };
  
  // ============================================
  // COMPUTED VALUE: isAuthenticated
  // ============================================
  
  /**
   * isAuthenticated - Convenience flag
   * 
   * Just a boolean: true if user exists, false otherwise
   * Saves components from having to check 'if (user !== null)'
   * 
   * They can just check: if (isAuthenticated) { ... }
   */
  const isAuthenticated = user !== null;
  
  // ============================================
  // CONTEXT VALUE
  // ============================================
  
  /**
   * The value we provide to all children
   * 
   * This object is what components get when they call useAuth()
   * 
   * Example usage in a component:
   * const { user, loading, login, logout, isAuthenticated } = useAuth();
   */
  const value: AuthContextType = {
    user,                // Current user object (or null)
    loading,             // True while checking auth status
    login,               // Function to start OAuth flow
    logout,              // Function to clear session
    isAuthenticated,     // Boolean for convenience
  };
  
  // ============================================
  // RENDER
  // ============================================
  
  /**
   * Return the Provider with our value
   * 
   * All children will be able to access 'value' via useAuth()
   * 
   * In App.tsx, we'll wrap everything with:
   * <AuthProvider>
   *   <App />
   * </AuthProvider>
   */
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// ============================================
// 3. CREATE THE HOOK
// ============================================

/**
 * useAuth() - Custom hook to access auth context
 * 
 * BIG PICTURE:
 * This is a convenience hook that components use to access auth state.
 * It handles the boilerplate of calling useContext(AuthContext).
 * 
 * USAGE IN COMPONENTS:
 * 
 * function Dashboard() {
 *   const { user, loading, logout } = useAuth();
 *   
 *   if (loading) return <div>Loading...</div>;
 *   if (!user) return <div>Please login</div>;
 *   
 *   return (
 *     <div>
 *       <h1>Welcome {user.name}!</h1>
 *       <button onClick={logout}>Logout</button>
 *     </div>
 *   );
 * }
 * 
 * ERROR HANDLING:
 * If someone tries to use useAuth() outside of <AuthProvider>,
 * we throw a helpful error instead of returning undefined.
 */
export const useAuth = (): AuthContextType => {
  // Get the context value
  const context = useContext(AuthContext);
  
  // Check if we're inside a Provider
  if (context === undefined) {
    throw new Error(
      'useAuth must be used within an AuthProvider. ' +
      'Make sure your App is wrapped with <AuthProvider>.'
    );
  }
  
  // Return the context value
  return context;
};

// ============================================
// SUMMARY OF FILES WORKING TOGETHER
// ============================================

/**
 * HOW THESE THREE FILES WORK TOGETHER:
 * 
 * 1. types/index.ts
 *    - Defines what a User looks like
 *    - Defines AuthContextType interface
 * 
 * 2. api/client.ts
 *    - Handles all HTTP requests to backend
 *    - Automatically adds auth token to requests
 *    - Handles 401 errors by redirecting to login
 * 
 * 3. context/AuthContext.tsx (this file)
 *    - Uses apiClient to fetch user data
 *    - Stores user in React state
 *    - Provides user data to all components
 *    - Provides login/logout functions
 * 
 * FLOW EXAMPLE: User visits the app
 * 
 * 1. App loads → AuthProvider mounts
 * 2. useEffect checks localStorage for token
 * 3. Token found → apiClient.get('/auth/me')
 * 4. apiClient adds token to request (via interceptor)
 * 5. Backend validates token, returns user data
 * 6. setUser(userData)
 * 7. All components can now access user via useAuth()
 * 8. User clicks "Logout" → logout() clears everything
 */
