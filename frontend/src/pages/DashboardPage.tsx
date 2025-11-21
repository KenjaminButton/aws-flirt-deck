/**
 * Dashboard Page Component
 * 
 * Main page users see after logging in.
 * Shows profile info and provides navigation to main features.
 */

import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

const DashboardPage = () => {
  const { user } = useAuth();
  
  if (!user) {
    return null;
  }
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back{user.name ? `, ${user.name.split(' ')[0]}` : ''}! 👋
          </h2>
          <p className="text-gray-600">
            Here's your 💕FlirtDecks dashboard
          </p>
        </div>
        
        {/* Subscription Status Card */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                Subscription Status
              </h3>
              <div className="flex items-center gap-2">
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  user.subscription_status === 'premium' 
                    ? 'bg-purple-100 text-purple-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {user.subscription_status === 'premium' ? '⭐ Premium' : '🆓 Free'}
                </span>
                {user.subscription_status === 'free' && (
                  <span className="text-sm text-gray-500">
                    (Limited to 1 connection)
                  </span>
                )}
              </div>
            </div>
            
            {user.subscription_status === 'free' && (
              <Link
                to="/billing"
                className="px-6 py-2 bg-purple-500 text-white font-semibold rounded-lg hover:bg-purple-600 transition duration-200"
              >
                Upgrade to Premium
              </Link>
            )}
          </div>
        </div>
        
        {/* Feature Cards Grid */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Questions Card */}
          <Link to="/questions" className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow border border-gray-200">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-4xl">💬</span>
              <div>
                <h3 className="text-xl font-bold text-gray-900">
                  Questions
                </h3>
                <p className="text-sm text-gray-500">
                  Browse conversation starters
                </p>
              </div>
            </div>
            
            <p className="text-gray-600 mb-4">
              Explore questions across life, random, deep, and experiences categories to keep your conversations flowing.
            </p>
            
            <div className="text-purple-600 font-medium">
              Browse Questions →
            </div>
          </Link>
          
          {/* Connections Card */}
          <Link to="/connections" className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow border border-gray-200">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-4xl">👥</span>
              <div>
                <h3 className="text-xl font-bold text-gray-900">
                  Connections
                </h3>
                <p className="text-sm text-gray-500">
                  Manage your conversations
                </p>
              </div>
            </div>
            
            <p className="text-gray-600 mb-4">
              Create connections for people you're talking to and track which questions you've used with each person.
            </p>
            
            <div className="text-purple-600 font-medium">
              Manage Connections →
            </div>
          </Link>
        </div>
        
        {/* Quick Stats */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Questions</p>
                <p className="text-2xl font-bold text-gray-900">12</p>
              </div>
              <span className="text-3xl">📝</span>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Connections</p>
                <p className="text-2xl font-bold text-gray-900">
                  {user.subscription_status === 'free' ? '0-1' : '∞'}
                </p>
              </div>
              <span className="text-3xl">👥</span>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Account Type</p>
                <p className="text-2xl font-bold text-gray-900">
                  {user.subscription_status === 'premium' ? 'Premium' : 'Free'}
                </p>
              </div>
              <span className="text-3xl">
                {user.subscription_status === 'premium' ? '⭐' : '🆓'}
              </span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;