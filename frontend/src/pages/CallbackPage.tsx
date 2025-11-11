import { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/client';
import type { User } from '../types/index';

// import { useAuth } from '../../context/AuthContext';
import { useAuth } from '../context/AuthContext';
/**
 * CallbackPage Component
 * 
 * Handles the OAuth callback and token exchange
 */
const CallbackPage = () => {
  // Navigation hook (for redirecting after successful login)
  const navigate = useNavigate();
  const { refreshUser } = useAuth();
  // State for showing loading/error messages
  const [status, setStatus] = useState<'loading' | 'error'>('loading');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const hasRun = useRef(false); 
  
  /**
   * Main effect: Runs once when component mounts
   * 
   * This is where all the OAuth magic happens
   */
  useEffect(() => {
    if (hasRun.current) return;
    hasRun.current = true;
    // Define an async function (can't use async directly in useEffect)
    const handleCallback = async () => {
      try {
        // ============================================
        // STEP 1: Extract authorization code from URL
        // ============================================
        
        /**
         * When Cognito redirects here, the URL looks like:
         * http://localhost:5173/auth/callback?code=abc123xyz&state=optional
         * 
         * We need to extract the 'code' parameter
         */
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        
        // Validate that we have a code
        if (!code) {
          throw new Error('No authorization code found in URL');
        }
        
        console.log('Authorization code received:', code.substring(0, 10) + '...');
        
        // ============================================
        // STEP 2: Exchange code for tokens
        // ============================================
        
        /**
         * Now we need to call Cognito's token endpoint to exchange
         * the authorization code for actual tokens (id, access, refresh).
         * 
         * This is a standard OAuth 2.0 token exchange.
         * 
         * IMPORTANT: We're calling COGNITO directly here, not our backend API!
         */
        
        // Get Cognito configuration from environment variables
        const cognitoDomain = import.meta.env.VITE_COGNITO_DOMAIN;
        const clientId = import.meta.env.VITE_COGNITO_CLIENT_ID;
        const redirectUri = import.meta.env.VITE_REDIRECT_URI;
        
        // Construct the token endpoint URL
        const tokenEndpoint = `https://${cognitoDomain}/oauth2/token`;
        
        /**
         * Prepare the request body
         * 
         * OAuth token endpoint expects application/x-www-form-urlencoded format
         * NOT JSON! This is important.
         * 
         * Parameters explained:
         * - grant_type: 'authorization_code' = we're exchanging a code for tokens
         * - client_id: identifies our app
         * - code: the authorization code we received
         * - redirect_uri: must EXACTLY match what we used in login (Cognito validates this)
         */
        const tokenRequestBody = new URLSearchParams({
          grant_type: 'authorization_code',
          client_id: clientId,
          code: code,
          redirect_uri: redirectUri,
        });
        
        console.log('Exchanging code for tokens...');
        
        /**
         * Make the token exchange request
         * 
         * NOTE: We use fetch() here instead of apiClient because:
         * 1. This is calling Cognito, not our backend
         * 2. We don't have tokens yet (can't use auth interceptor)
         * 3. Content-Type must be application/x-www-form-urlencoded
         */
        const tokenResponse = await fetch(tokenEndpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: tokenRequestBody.toString(),
        });
        
        // Check if request was successful
        if (!tokenResponse.ok) {
          const errorData = await tokenResponse.json();
          throw new Error(`Token exchange failed: ${errorData.error || tokenResponse.statusText}`);
        }
        
        // Parse the response to get tokens
        const tokens = await tokenResponse.json();
        
        console.log('Tokens received successfully!');
        
        // ============================================
        // STEP 3: Store tokens in localStorage
        // ============================================
        
        /**
         * Store all three tokens
         * 
         * - id_token: Contains user claims (email, name, etc.) - This is what we send to our API
         * - access_token: Used for Cognito APIs (we don't use this much)
         * - refresh_token: Used to get new tokens when they expire (1 hour lifespan)
         * 
         * WHY localStorage:
         * - Simple and works across tabs
         * - Survives page refresh
         * - Accessible by our API client
         * 
         * SECURITY NOTE:
         * For production, consider more secure storage (httpOnly cookies, etc.)
         * But for a portfolio project, localStorage is fine.
         */
        localStorage.setItem('idToken', tokens.id_token);
        localStorage.setItem('accessToken', tokens.access_token);
        localStorage.setItem('refreshToken', tokens.refresh_token);
        
        console.log('Tokens stored in localStorage');
        
        // ============================================
        // STEP 4: Fetch user profile from our backend
        // ============================================
        
        /**
         * Now that we have tokens, call our backend to get/create user profile
         * 
         * This hits GET /auth/me which:
         * 1. Validates the token
         * 2. Extracts user ID from token
         * 3. Fetches or creates user profile in DynamoDB
         * 4. Returns user data
         * 
         * NOTE: apiClient will automatically add the idToken to this request
         * (via the request interceptor we set up in client.ts)
         */
        console.log('Fetching user profile...');
        
        const userResponse = await apiClient.get<User>('/auth/me');
        const user = userResponse.data;
        
        console.log('User profile loaded:', user.email);
        
        // Force AuthContext to refresh
        await refreshUser();

        console.log('Login successful! Redirecting to dashboard...');
        // Small delay to ensure AuthContext has time to process the token
        await new Promise(resolve => setTimeout(resolve, 500));
        navigate('/dashboard');
        
      } catch (error: any) {
        // ============================================
        // ERROR HANDLING
        // ============================================
        
        /**
         * Something went wrong. Common causes:
         * - Invalid authorization code (expired or already used)
         * - Wrong redirect_uri (doesn't match Google Console settings)
         * - Network error
         * - Backend API error
         * 
         * Show user-friendly error message and suggest retry
         */
        console.error('Login error:', error);
        
        setStatus('error');
        setErrorMessage(
          error.message || 'Failed to complete login. Please try again.'
        );
      }
    };
    
    // Run the callback handler
    handleCallback();
  }, []); // Empty dependency array = run once on mount
  
  // ============================================
  // RENDER UI
  // ============================================
  
  /**
   * Show different UI based on status:
   * - loading: Show spinner while processing
   * - error: Show error message with retry button
   */
  
  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-500 to-pink-500">
        <div className="bg-white p-8 rounded-lg shadow-2xl max-w-md w-full text-center">
          {/* Loading spinner */}
          <div className="mb-4">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-500 mx-auto"></div>
          </div>
          
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Completing Sign In...
          </h2>
          
          <p className="text-gray-600">
            Please wait while we set up your account
          </p>
          
          {/* Technical details for debugging (remove in production) */}
          <p className="text-xs text-gray-400 mt-4">
            Exchanging authorization code for tokens
          </p>
        </div>
      </div>
    );
  }
  
  // Error state
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-500 to-pink-500">
      <div className="bg-white p-8 rounded-lg shadow-2xl max-w-md w-full text-center">
        {/* Error icon */}
        <div className="text-6xl mb-4">❌</div>
        
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          Login Failed
        </h2>
        
        <p className="text-gray-600 mb-6">
          {errorMessage}
        </p>
        
        {/* Retry button - redirects back to login page */}
        <button
          onClick={() => navigate('/login')}
          className="w-full bg-purple-500 text-white font-semibold py-3 px-4 rounded-lg hover:bg-purple-600 transition duration-200"
        >
          Try Again
        </button>
        
        {/* Help text */}
        <p className="text-xs text-gray-500 mt-4">
          If this problem persists, check your internet connection or contact support.
        </p>
      </div>
    </div>
  );
};

export default CallbackPage;