import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import apiClient from '../api/client'
import CreateConnectionModal from '../components/connections/CreateConnectionModal';



interface Connection {
  id: string;
  name: string;
  created_at: string;
  usage_count?: number; 
}

const ConnectionsPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate(); 
  const [connections, setConnections] = useState<Connection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  

  // Fetch connections on mount
  useEffect(() => {
    fetchConnections();
  }, []);

  const fetchConnections = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.get('/connections');
      setConnections(response.data);
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

  // ✨ NEW: Handle clicking on a connection card
  const handleCardClick = (connectionId: string) => {
    // Navigate to the detail page for this connection
    navigate(`/connections/${connectionId}`);
  };

  const handleDelete = async (connectionId: string, connectionName: string) => {
    if (!confirm(`Delete "${connectionName}"? This cannot be undone.`)) {
      return;
    }

    setDeletingId(connectionId);

    try {
      await apiClient.delete(`/connections/${connectionId}`);
      
      // Refresh the list
      await fetchConnections();
    } catch (err) {
      console.error('Error deleting connection:', err);
      alert('Failed to delete connection. Please try again.');
    } finally {
      setDeletingId(null);
    }
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
                // ✨ NEW: Add onClick handler to make card clickable
                onClick={() => handleCardClick(connection.id)}
                // ✨ NEW: Enhanced hover effects for better UX
                className="bg-white rounded-xl shadow-lg p-6 hover:shadow-2xl transition-all cursor-pointer border-2 border-transparent hover:border-purple-300 transform hover:-translate-y-1"
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

                  {/* Delete Button */}
                  <button
                    onClick={(e) => {
                      // ✨ CRITICAL: Stop event from bubbling to card
                      // This prevents navigating when clicking delete
                      e.stopPropagation();
                      handleDelete(connection.id, connection.name);
                    }}
                    disabled={deletingId === connection.id}
                    className="text-red-400 hover:text-red-600 text-sm font-medium px-4 py-2 rounded-lg hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {deletingId === connection.id ? '...' : '🗑️ Delete'}
                  </button>
                </div>

                {/* Stats (placeholder for future features) */}
                <div className="mt-4 flex gap-4 text-sm text-gray-600">
                  <span>📝 {connection.usage_count || 0} questions answered</span>
                </div>
                
                {/* ✨ NEW: Visual indicator that card is clickable */}
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <span className="text-xs text-purple-600 font-medium">
                    👉 Click to view details
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Free Tier Info */}
        {connections.length > 0 && user.subscription_status === 'free' && (
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
