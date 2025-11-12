import { useParams, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';

interface Connection {
  id: string;
  name: string;
  created_at: string;
}

export default function ConnectionDetailPage() {
  const { connectionId } = useParams<{ connectionId: string }>();
  const navigate = useNavigate();
  const { getAuthToken } = useAuth();
  
  const [connection, setConnection] = useState<Connection | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchConnection = async () => {
      try {
        const token = await getAuthToken();
        const apiUrl = import.meta.env.VITE_API_URL;

        const response = await fetch(`${apiUrl}/connections`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          }
        });

        if (!response.ok) throw new Error('Failed to fetch');

        const connections = await response.json();
        const found = connections.find((c: Connection) => c.id === connectionId);

        if (!found) {
          setError('Connection not found');
        } else {
          setConnection(found);
        }
      } catch (err) {
        setError('Failed to load connection');
      } finally {
        setLoading(false);
      }
    };

    fetchConnection();
  }, [connectionId, getAuthToken]);

  const handleBack = () => {
    navigate('/connections');
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
        </div>
      </div>
    );
  }

  if (error || !connection) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-red-800 mb-2">
            Error Loading Connection
          </h2>
          <p className="text-red-600 mb-4">
            {error || 'Connection not found'}
          </p>
          <button
            onClick={handleBack}
            className="bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600"
          >
            ← Back to Connections
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <button
        onClick={handleBack}
        className="flex items-center text-gray-600 hover:text-purple-600 mb-4"
      >
        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Back to Connections
      </button>

      <h1 className="text-3xl font-bold text-gray-800">
        {connection.name}
      </h1>
      
      <p className="text-gray-500 mt-2">
        Created: {new Date(connection.created_at).toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
        })}
      </p>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6 mt-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Connection Details
        </h2>
        
        <div className="space-y-3">
          <div>
            <span className="text-gray-600 font-medium">Name:</span>
            <span className="ml-2 text-gray-800">{connection.name}</span>
          </div>
          
          <div>
            <span className="text-gray-600 font-medium">Connection ID:</span>
            <span className="ml-2 text-gray-800 font-mono text-sm">
              {connection.id}
            </span>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Question Usage
        </h2>
        
        <div className="bg-white rounded-lg p-6 text-center">
          <div className="text-5xl font-bold text-purple-500 mb-2">
            0
          </div>
          <p className="text-gray-600">
            Questions used with {connection.name}
          </p>
          
          <div className="mt-4 inline-block bg-purple-100 text-purple-700 px-4 py-2 rounded-full text-sm font-medium">
            🚀 Usage tracking coming soon!
          </div>
        </div>
      </div>

      <div className="mt-6">
        <button
          onClick={handleBack}
          className="bg-purple-500 text-white px-6 py-3 rounded-lg hover:bg-purple-600 font-medium"
        >
          ← Back to All Connections
        </button>
      </div>
    </div>
  );
}

