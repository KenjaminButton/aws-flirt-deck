/**
 * Dashboard Page Component
 * 
 * BIG PICTURE:
 * This is the main page users see after logging in.
 * It displays their profile info and provides navigation to main features.
 * 
 * Currently shows:
 * - User name and email
 * - Subscription status
 * - Logout button
 * - Placeholders for Questions and Connections (will be built in later days)
 * 
 * ANALOGY:
 * Think of this as the "home screen" of your app - like the main dashboard
 * in any SaaS app (Gmail, Notion, etc.) where you see your stuff and can
 * navigate to different sections.
 */

import { useAuth } from '../context/AuthContext';

const DashboardPage = () => {
  // Get authentication data from context
  const { user, logout } = useAuth();
  
  // This shouldn't happen (ProtectedRoute prevents it), but TypeScript needs the check
  if (!user) {
    return null;
  }
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header / Navigation Bar */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            {/* Logo / App Name */}
            <h1 className="text-2xl font-bold text-purple-600">
              FlirtDeck
            </h1>
            
            {/* User Info & Logout */}
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  {user.name || 'User'}
                </p>
                <p className="text-xs text-gray-500">
                  {user.email}
                </p>
              </div>
              
              <button
                onClick={logout}
                className="px-4 py-2 text-sm font-medium text-white bg-red-500 rounded-lg hover:bg-red-600 transition duration-200"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back{user.name ? `, ${user.name.split(' ')[0]}` : ''}! 👋
          </h2>
          <p className="text-gray-600">
            Here's your FlirtDeck dashboard
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
              <button
                className="px-6 py-2 bg-purple-500 text-white font-semibold rounded-lg hover:bg-purple-600 transition duration-200"
                onClick={() => alert('Upgrade feature coming in Phase 5!')}
              >
                Upgrade to Premium
              </button>
            )}
          </div>
        </div>
        
        {/* Feature Cards Grid */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Questions Card */}
          <div className="bg-white rounded-lg shadow-sm p-6 border-2 border-dashed border-gray-300">
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
            
            <button
              className="w-full py-2 px-4 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 transition duration-200"
              onClick={() => alert('Questions feature coming on Day 11-12!')}
            >
              Coming Soon: Day 11-12
            </button>
          </div>
          
          {/* Connections Card */}
          <div className="bg-white rounded-lg shadow-sm p-6 border-2 border-dashed border-gray-300">
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
            
            <button
              className="w-full py-2 px-4 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 transition duration-200"
              onClick={() => alert('Connections feature coming on Day 13-15!')}
            >
              Coming Soon: Day 13-15
            </button>
          </div>
        </div>
        
        {/* Info Box */}
        <div className="mt-8 bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
          <div className="flex">
            <div className="flex-shrink-0">
              <span className="text-2xl">ℹ️</span>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-900">
                Development Progress
              </h3>
              <div className="mt-2 text-sm text-blue-700">
                <ul className="list-disc list-inside space-y-1">
                  <li>✅ Day 8: Frontend setup complete</li>
                  <li>✅ Day 9: Authentication working</li>
                  <li>✅ Day 10: Dashboard created</li>
                  <li>⏳ Day 11-12: Questions system (next)</li>
                  <li>⏳ Day 13-15: Connections management</li>
                  <li>⏳ Day 16-18: Stripe billing integration</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;
