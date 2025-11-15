/**
 * Billing Success Page
 * 
 * Shown after user successfully completes Stripe checkout.
 * Note: Subscription is not yet active - webhook handles activation.
 */

import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

const BillingSuccessPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    // Auto-redirect to dashboard after 5 seconds
    const timer = setTimeout(() => {
      navigate('/dashboard');
    }, 5000);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 text-center">
        {/* Success Icon */}
        <div className="mb-6">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto">
            <span className="text-5xl">✓</span>
          </div>
        </div>

        {/* Title */}
        <h1 className="text-3xl font-bold text-gray-900 mb-3">
          Payment Successful! 🎉
        </h1>

        {/* Message */}
        <p className="text-gray-600 mb-6">
          Thank you for upgrading to Premium! Your subscription will be activated shortly.
        </p>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-blue-800">
            <strong>⏳ Processing payment...</strong>
          </p>
          <p className="text-sm text-blue-700 mt-2">
            Your premium features will be available within 1-2 minutes. 
            We're activating your subscription now.
          </p>
        </div>

        {/* Session ID (for support) */}
        {sessionId && (
          <div className="mb-6">
            <p className="text-xs text-gray-500">
              Session ID: {sessionId.substring(0, 20)}...
            </p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="space-y-3">
          <button
            onClick={() => navigate('/dashboard')}
            className="w-full px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold rounded-xl shadow-lg transition-all"
          >
            Go to Dashboard
          </button>
          
          <button
            onClick={() => navigate('/connections')}
            className="w-full px-6 py-3 border-2 border-purple-300 text-purple-600 hover:bg-purple-50 font-medium rounded-xl transition-colors"
          >
            Create Unlimited Connections
          </button>
        </div>

        {/* Auto-redirect notice */}
        <p className="text-xs text-gray-400 mt-6">
          Redirecting to dashboard in 5 seconds...
        </p>
      </div>
    </div>
  );
};

export default BillingSuccessPage;