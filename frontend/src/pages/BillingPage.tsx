/**
 * Billing Page Component
 * 
 * MVP Version: Shows subscription status and upgrade option
 * Phase 6: Will integrate with Stripe for actual payments
 * 
 * Features:
 * - Display current plan (Free/Premium)
 * - Show plan benefits comparison
 * - Upgrade button (placeholder for Stripe integration)
 * - Cancel subscription button (if premium)
 */

import { useAuth } from '../context/AuthContext';

const BillingPage = () => {
  const { user } = useAuth();

  if (!user) {
    return null;
  }

  const isPremium = user.subscription_status === 'premium';

  // Placeholder functions for Phase 6 Stripe integration
  const handleUpgrade = () => {
    alert('💳 Stripe integration coming in Phase 6!\n\nThis will redirect you to Stripe Checkout to upgrade to Premium.');
  };

  const handleCancelSubscription = () => {
    if (confirm('Are you sure you want to cancel your Premium subscription?\n\n(This is a placeholder - actual cancellation coming in Phase 6)')) {
      alert('Subscription cancellation will be implemented in Phase 6 with Stripe.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 py-12 px-4">
      <div className="max-w-5xl mx-auto">
        
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">💳 Billing</h1>
          <p className="text-gray-600">Manage your subscription and billing</p>
        </div>

        {/* Current Plan Card */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Current Plan</h2>
          
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <span className={`text-3xl ${isPremium ? '⭐' : '🆓'}`}>
                  {isPremium ? '⭐' : '🆓'}
                </span>
                <div>
                  <h3 className="text-2xl font-bold text-gray-900">
                    {isPremium ? 'Premium' : 'Free'}
                  </h3>
                  <p className="text-gray-600">
                    {isPremium ? '$2.99/month' : 'Limited features'}
                  </p>
                </div>
              </div>
              
              {isPremium && (
                <p className="text-sm text-gray-500 mt-2">
                  📅 Next billing date: Coming soon
                </p>
              )}
            </div>

            {!isPremium ? (
              <button
                onClick={handleUpgrade}
                className="px-8 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold rounded-xl shadow-lg transform transition-all hover:scale-105"
              >
                ⭐ Upgrade to Premium
              </button>
            ) : (
              <button
                onClick={handleCancelSubscription}
                className="px-6 py-3 border-2 border-red-300 text-red-600 hover:bg-red-50 font-medium rounded-xl transition-colors"
              >
                Cancel Subscription
              </button>
            )}
          </div>
        </div>

        {/* Plan Comparison */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          
          {/* Free Plan */}
          <div className={`bg-white rounded-2xl shadow-lg p-8 ${!isPremium ? 'ring-2 ring-purple-500' : ''}`}>
            <div className="flex items-center gap-2 mb-4">
              <span className="text-3xl">🆓</span>
              <h3 className="text-2xl font-bold text-gray-900">Free</h3>
            </div>
            
            <p className="text-3xl font-bold text-gray-900 mb-6">
              $0<span className="text-lg font-normal text-gray-600">/month</span>
            </p>

            <ul className="space-y-3 mb-6">
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-1">✓</span>
                <span className="text-gray-700">1 connection maximum</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-1">✓</span>
                <span className="text-gray-700">Access to all question categories</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-1">✓</span>
                <span className="text-gray-700">Basic conversation tracking</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-red-500 mt-1">✗</span>
                <span className="text-gray-400">Unlimited connections</span>
              </li>
            </ul>

            {!isPremium && (
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                <p className="text-sm text-purple-800 font-medium">Current Plan</p>
              </div>
            )}
          </div>

          {/* Premium Plan */}
          <div className={`bg-white rounded-2xl shadow-lg p-8 ${isPremium ? 'ring-2 ring-purple-500' : ''}`}>
            <div className="flex items-center gap-2 mb-4">
              <span className="text-3xl">⭐</span>
              <div>
                <h3 className="text-2xl font-bold text-gray-900">Premium</h3>
                <span className="inline-block bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs font-semibold px-2 py-1 rounded-full">
                  MOST POPULAR
                </span>
              </div>
            </div>
            
            <p className="text-3xl font-bold text-gray-900 mb-6">
              $2.99<span className="text-lg font-normal text-gray-600">/month</span>
            </p>

            <ul className="space-y-3 mb-6">
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-1">✓</span>
                <span className="text-gray-700"><strong>Unlimited connections</strong></span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-1">✓</span>
                <span className="text-gray-700">Access to all question categories</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-1">✓</span>
                <span className="text-gray-700">Advanced conversation tracking</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-1">✓</span>
                <span className="text-gray-700">Priority support</span>
              </li>
            </ul>

            {isPremium ? (
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                <p className="text-sm text-purple-800 font-medium">✓ Active Plan</p>
              </div>
            ) : (
              <button
                onClick={handleUpgrade}
                className="w-full px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold rounded-xl shadow-lg transform transition-all hover:scale-105"
              >
                Upgrade Now
              </button>
            )}
          </div>
        </div>

        {/* Info Notice */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
          <p className="text-sm text-blue-800">
            💡 <strong>Phase 6 Preview:</strong> Stripe integration coming soon for secure payments and subscription management.
          </p>
        </div>
      </div>
    </div>
  );
};

export default BillingPage;