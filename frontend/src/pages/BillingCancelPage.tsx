/**
 * Billing Cancel Page
 * 
 * Shown when user cancels Stripe checkout.
 */

import { useNavigate } from 'react-router-dom';

const BillingCancelPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 text-center">
        {/* Cancel Icon */}
        <div className="mb-6">
          <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto">
            <span className="text-5xl">✕</span>
          </div>
        </div>

        {/* Title */}
        <h1 className="text-3xl font-bold text-gray-900 mb-3">
          Checkout Cancelled
        </h1>

        {/* Message */}
        <p className="text-gray-600 mb-6">
          No worries! Your upgrade was cancelled and you have not been charged.
        </p>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-blue-800">
            💡 <strong>Still want to upgrade?</strong>
          </p>
          <p className="text-sm text-blue-700 mt-2">
            Premium gives you unlimited connections and advanced features for just $2.99/month.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <button
            onClick={() => navigate('/billing')}
            className="w-full px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold rounded-xl shadow-lg transition-all"
          >
            Try Again - Upgrade to Premium
          </button>
          
          <button
            onClick={() => navigate('/dashboard')}
            className="w-full px-6 py-3 border-2 border-gray-300 text-gray-700 hover:bg-gray-50 font-medium rounded-xl transition-colors"
          >
            Back to Dashboard
          </button>
        </div>

        {/* Help Text */}
        <p className="text-xs text-gray-500 mt-6">
          Questions? Contact us at{' '}
          <a href="mailto:support@flirtdeck.com" className="text-purple-600 hover:underline">
            support@flirtdeck.com
          </a>
        </p>
      </div>
    </div>
  );
};

export default BillingCancelPage;