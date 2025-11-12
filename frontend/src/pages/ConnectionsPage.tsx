/**
 * Connections Page Component
 * 
 * Main page for managing conversation partners (connections).
 * Shows list of connections and allows creating new ones.
 * 
 * Features:
 * - List all connections
 * - Create new connection (with free tier limit)
 * - Click connection to view details (future)
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import CreateConnectionModal from '../components/connections/CreateConnectionModal';

interface Connection {
  id: string;
  name: string;
  created_at: string;
}

const ConnectionsPage: React.FC = () => {
  const { getAuthToken } = useAuth();
  
  const [connections, setConnections] = useState<Connection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);

  // Fetch connections on mount
  useEffect(() => {
    fetchConnections();
  }, []);

  const fetchConnections = async () => {
    setLoading(true);
    setError(null);

    try {
      const token = await getAuthToken();
      const apiUrl = import.meta.env.VITE_API_URL;

      const response = await fetch(`${apiUrl}/connections`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch connections');
      }

      const data = await response.json();
      setConnections(data);
      
    } catch (err) {
      console.error('Error fetching connections:', err);
      setError('Failed to load connections');
    } finally {
      setLoading(false);
    }
  };

  const handleConnectionCreated = () => {
    // Refresh the list after creating a new connection
    fetchConnections();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              💬 My Connections
            </h1>
            <p className="text-gray-600">
              Manage your conversation partners
            </p>
          </div>
          
          <button
            onClick={() => setShowModal(true)}
            className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold py-3 px-6 rounded-xl shadow-lg transform transition-all hover:scale-105 active:scale-95"
          >
            ➕ Add Connection
          </button>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-2xl shadow-xl p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent mb-4"></div>
            <p className="text-gray-600 text-lg">Loading connections...</p>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-6 text-center">
            <span className="text-4xl mb-3 block">⚠️</span>
            <p className="text-red-700 font-medium">{error}</p>
            <button
              onClick={fetchConnections}
              className="mt-4 bg-red-500 hover:bg-red-600 text-white font-medium py-2 px-6 rounded-lg"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && connections.length === 0 && (
          <div className="bg-white rounded-2xl shadow-xl p-12 text-center">
            <span className="text-6xl mb-4 block">👥</span>
            <h3 className="text-2xl font-bold text-gray-800 mb-3">
              No connections yet
            </h3>
            <p className="text-gray-600 text-lg mb-6">
              Create your first connection to start tracking conversations!
            </p>
            <button
              onClick={() => setShowModal(true)}
              className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold py-3 px-8 rounded-xl shadow-lg transform transition-all hover:scale-105"
            >
              ➕ Create First Connection
            </button>
          </div>
        )}

        {/* Connections List */}
        {!loading && !error && connections.length > 0 && (
          <div className="space-y-4">
            {connections.map((connection) => (
              <div
                key={connection.id}
                className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer border-2 border-transparent hover:border-purple-200"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    {/* Avatar */}
                    <div className="w-12 h-12 bg-gradient-to-br from-purple-400 to-pink-400 rounded-full flex items-center justify-center text-white font-bold text-xl">
                      {connection.name.charAt(0).toUpperCase()}
                    </div>
                    
                    {/* Info */}
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900">
                        {connection.name}
                      </h3>
                      <p className="text-sm text-gray-500">
                        Created {new Date(connection.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>

                  {/* Action Button (placeholder for future) */}
                  <button className="text-gray-400 hover:text-gray-600 text-2xl">
                    →
                  </button>
                </div>

                {/* Stats (placeholder for future features) */}
                <div className="mt-4 flex gap-4 text-sm text-gray-600">
                  <span>📝 0 questions answered</span>
                  <span>🗒️ 0 notes</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Free Tier Info */}
        {connections.length > 0 && (
          <div className="mt-6 p-4 bg-blue-50 rounded-xl">
            <p className="text-sm text-blue-700">
              💡 <span className="font-medium">You have {connections.length} connection{connections.length !== 1 ? 's' : ''}</span>
            </p>
            {connections.length >= 1 && (
              <p className="text-sm text-blue-700 mt-1">
                Free tier limit reached. Upgrade to Premium for unlimited connections!
              </p>
            )}
          </div>
        )}

        {/* Create Connection Modal */}
        <CreateConnectionModal
          isOpen={showModal}
          onClose={() => setShowModal(false)}
          onSuccess={handleConnectionCreated}
        />
      </div>
    </div>
  );
};

export default ConnectionsPage;
