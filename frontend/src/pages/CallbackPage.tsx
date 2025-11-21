import { useEffect, useState, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import apiClient from '../api/client';
import { useAuth } from '../context/AuthContext';

const CallbackPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { refreshUser } = useAuth();
  const [error, setError] = useState<string>('');

const hasRun = useRef(false);

useEffect(() => {
  if (hasRun.current) return;
  hasRun.current = true;

  const handleCallback = async () => {
    console.log('=== CALLBACK STARTED ===');
    console.log('Full URL:', window.location.href);
    
    const code = searchParams.get('code');
    const errorParam = searchParams.get('error');
    
    console.log('Code:', code);
    console.log('Error param:', errorParam);

    if (errorParam) {
      console.log('OAuth error detected');
      setError(`Authentication failed: ${errorParam}`);
      return;
    }

    if (!code) {
      console.log('No code found in URL');
      setError('No authorization code received');
      return;
    }

    try {
      console.log('Calling /auth/token endpoint...');
      const response = await apiClient.post('/auth/token', { 
        code,
        redirect_uri: import.meta.env.VITE_COGNITO_REDIRECT_URI 
      });
      console.log('Token response:', response.data);
      
      const { id_token, access_token, refresh_token } = response.data;

      console.log('Storing tokens...');
      localStorage.setItem('idToken', id_token);
      localStorage.setItem('accessToken', access_token);
      if (refresh_token) {
        localStorage.setItem('refreshToken', refresh_token);
      }

      console.log('Refreshing user...');
      await refreshUser();
      
      console.log('User loaded, waiting for auth state...');
      await new Promise(resolve => setTimeout(resolve, 1000));

      console.log('Navigating to dashboard...');
      window.location.href = '/dashboard';

    } catch (err: any) {
      console.error('=== ERROR ===', err);
      console.error('Error response:', err.response?.data);
      console.error('Error status:', err.response?.status);
      setError('Login failed: ' + (err.response?.data?.error || err.message));
    }
  };

  handleCallback();
}, []);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-500 to-pink-500">
        <div className="bg-white p-8 rounded-lg shadow-2xl max-w-md w-full text-center">
          <div className="text-6xl mb-4">❌</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Login Failed</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => navigate('/login')}
            className="w-full bg-purple-500 text-white font-semibold py-3 px-4 rounded-lg hover:bg-purple-600 transition duration-200"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-500 to-pink-500">
      <div className="bg-white p-8 rounded-lg shadow-2xl max-w-md w-full text-center">
        <div className="mb-4">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-500 mx-auto"></div>
        </div>
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Completing Sign In...</h2>
        <p className="text-gray-600">Please wait while we set up your account</p>
      </div>
    </div>
  );
};

export default CallbackPage;