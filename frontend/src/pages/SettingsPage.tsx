/**
 * Settings Page Component
 * 
 * MVP Version: Shows basic account information
 * Future: Delete account, notification preferences, etc.
 */

import { useAuth } from '../context/AuthContext';

const SettingsPage = () => {
  const { user } = useAuth();

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">⚙️ Settings</h1>
          <p className="text-gray-600">Manage your account settings</p>
        </div>

        {/* Account Information Card */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
            <span>👤</span>
            Account Information
          </h2>

          <div className="space-y-6">
            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-2">
                Name
              </label>
              <div className="px-4 py-3 bg-gray-50 rounded-lg border border-gray-200">
                <p className="text-gray-900">
                  {user.name || 'Not provided'}
                </p>
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-2">
                Email
              </label>
              <div className="px-4 py-3 bg-gray-50 rounded-lg border border-gray-200">
                <p className="text-gray-900">{user.email}</p>
              </div>
            </div>

            {/* Account Created */}
            {user.created_at && (
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-2">
                  Member Since
                </label>
                <div className="px-4 py-3 bg-gray-50 rounded-lg border border-gray-200">
                  <p className="text-gray-900">
                    {new Date(user.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </p>
                </div>
              </div>
            )}

            {/* User ID (for debugging/support) */}
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-2">
                User ID
              </label>
              <div className="px-4 py-3 bg-gray-50 rounded-lg border border-gray-200">
                <p className="text-xs text-gray-500 font-mono break-all">
                  {user.user_id}
                </p>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                💡 Use this ID when contacting support
              </p>
            </div>
          </div>
        </div>

        {/* Info Notice */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            ℹ️ Account information is managed through your Google account. 
            To update your name or email, please update your Google profile.
          </p>
        </div>

        {/* Future Features Placeholder */}
        <div className="mt-6 text-center text-gray-400 text-sm">
          More settings coming soon: Delete account, notification preferences, and more!
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
