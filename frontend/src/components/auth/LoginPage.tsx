import { useAuth } from '../../context/AuthContext';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; 

/**
 * LoginPage Component
 * 
 * Displays the login UI and handles redirect for already-authenticated users
 */
const LoginPage = () => {
  // Get auth functions from our context
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate(); // Add this line
  /**
   * Redirect if already logged in
   * 
   * WHY: If someone navigates to /login while already authenticated,
   * we should send them to the dashboard instead.
   * 
   * This prevents the weird UX of seeing a login button when you're
   * already logged in.
   */
  useEffect(() => {
    if (isAuthenticated) {
      // User is already logged in, send them to dashboard
      // window.location.href = '/dashboard';
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);
  
  /**
   * Handle login button click
   * 
   * This calls the login() function from AuthContext, which:
   * 1. Constructs the Cognito OAuth URL
   * 2. Redirects the browser to Cognito/Google
   */
  const handleLogin = () => {
    login();
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-500 to-pink-500">
      {/* Main card container */}
      <div className="bg-white p-8 rounded-lg shadow-2xl max-w-md w-full">
        {/* App branding */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            💕FlirtDecks
          </h1>
          <p className="text-gray-600">
            Never run out of things to say
          </p>
        </div>
        
        {/* Feature highlights */}
        <div className="mb-8 space-y-3">
          <div className="flex items-start">
            <span className="text-2xl mr-3">💬</span>
            <div>
              <h3 className="font-semibold text-gray-800">Conversation Starters</h3>
              <p className="text-sm text-gray-600">
                Browse questions across life, random, deep, and experiences
              </p>
            </div>
          </div>
          
          <div className="flex items-start">
            <span className="text-2xl mr-3">📝</span>
            <div>
              <h3 className="font-semibold text-gray-800">Track Conversations</h3>
              <p className="text-sm text-gray-600">
                Remember what you talked about with each connection
              </p>
            </div>
          </div>
          
          <div className="flex items-start">
            <span className="text-2xl mr-3">✨</span>
            <div>
              <h3 className="font-semibold text-gray-800">Stay Organized</h3>
              <p className="text-sm text-gray-600">
                Keep all your dating conversations in one place
              </p>
            </div>
          </div>
        </div>
        
        {/* Login button */}
        <button
          onClick={handleLogin}
          className="w-full bg-white border-2 border-gray-300 text-gray-700 font-semibold py-3 px-4 rounded-lg hover:bg-gray-50 hover:border-gray-400 transition duration-200 flex items-center justify-center shadow-sm"
        >
          {/* Google logo (using emoji for simplicity - you could use an actual logo image) */}
          <span className="text-2xl mr-3">🔐</span>
          Sign in with Google
        </button>
        
        {/* Fine print */}
        <p className="text-xs text-gray-500 text-center mt-6">
          By signing in, you agree to our Terms of Service and Privacy Policy
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
