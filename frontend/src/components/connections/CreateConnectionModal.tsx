/**
 * Create Connection Modal Component
 * 
 * Allows users to create a new connection (conversation partner).
 * Shows error if free tier limit is reached (paywall).
 */

import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';

interface CreateConnectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const CreateConnectionModal: React.FC<CreateConnectionModalProps> = ({
  isOpen,
  onClose,
  onSuccess
}) => {
  const { getAuthToken } = useAuth();
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPaywallError, setIsPaywallError] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name.trim()) {
      setError('Please enter a name');
      return;
    }

    setLoading(true);
    setError(null);
    setIsPaywallError(false);

    try {
      const token = await getAuthToken();
      const apiUrl = import.meta.env.VITE_API_URL;

      const response = await fetch(`${apiUrl}/connections`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: name.trim() })
      });

      const data = await response.json();

      if (!response.ok) {
        // Check if it's a paywall error
        if (response.status === 403 && data.code === 'FREE_TIER_LIMIT') {
          setIsPaywallError(true);
          setError(data.error);
        } else {
          setError(data.error || 'Failed to create connection');
        }
        return;
      }

      // Success!
      setName('');
      onSuccess();
      onClose();
      
    } catch (err) {
      console.error('Error creating connection:', err);
      setError('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setName('');
    setError(null);
    setIsPaywallError(false);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6">
        
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            Add Connection
          </h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
              Name
            </label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Sarah from Hinge"
              maxLength={100}
              disabled={loading}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <p className="mt-1 text-sm text-gray-500">
              {name.length}/100 characters
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className={`mb-4 p-4 rounded-lg ${isPaywallError ? 'bg-yellow-50 border-2 border-yellow-200' : 'bg-red-50 border-2 border-red-200'}`}>
              <div className="flex items-start">
                <span className="text-2xl mr-3">
                  {isPaywallError ? '🔒' : '⚠️'}
                </span>
                <div>
                  <p className={`font-medium ${isPaywallError ? 'text-yellow-800' : 'text-red-800'}`}>
                    {isPaywallError ? 'Upgrade Required' : 'Error'}
                  </p>
                  <p className={`text-sm ${isPaywallError ? 'text-yellow-700' : 'text-red-700'}`}>
                    {error}
                  </p>
                  {isPaywallError && (
                    <button
                      type="button"
                      className="mt-2 text-sm font-medium text-purple-600 hover:text-purple-700 underline"
                      onClick={() => alert('Upgrade feature coming soon!')}
                    >
                      Upgrade to Premium
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Buttons */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={handleClose}
              disabled={loading}
              className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !name.trim()}
              className="flex-1 px-4 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium rounded-lg hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed transform transition-all hover:scale-105 active:scale-95"
            >
              {loading ? 'Creating...' : 'Create'}
            </button>
          </div>
        </form>

        {/* Free Tier Info */}
        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
          <p className="text-xs text-blue-700">
            💡 <span className="font-medium">Free Tier:</span> 1 connection
          </p>
          <p className="text-xs text-blue-700 mt-1">
            <span className="font-medium">Premium:</span> Unlimited connections
          </p>
        </div>
      </div>
    </div>
  );
};

export default CreateConnectionModal;
