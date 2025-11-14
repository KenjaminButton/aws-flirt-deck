import { useParams, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import apiClient from '../api/client';

interface Connection {
  id: string;
  name: string;
  created_at: string;
}

interface Question {
  id: string;
  text: string;
  category: string;
}

interface UsageRecord {
  usage_id: string;
  question_id: string;
  question_text: string;
  category?: string;
  their_answer: string;
  my_answer: string;
  created_at: string;
}

type Category = 'life' | 'random' | 'deep' | 'experiences';

const CATEGORIES: Record<Category, { name: string; color: string; emoji: string }> = {
  life: { name: 'Life', color: 'bg-blue-500 hover:bg-blue-600', emoji: '🌱' },
  random: { name: 'Random', color: 'bg-purple-500 hover:bg-purple-600', emoji: '🎲' },
  deep: { name: 'Deep', color: 'bg-indigo-500 hover:bg-indigo-600', emoji: '🤔' },
  experiences: { name: 'Experiences', color: 'bg-pink-500 hover:bg-pink-600', emoji: '✨' }
};

export default function ConnectionDetailPage() {
  const { connectionId } = useParams<{ connectionId: string }>();
  const navigate = useNavigate();
  const { getAuthToken } = useAuth();
  
  const [connection, setConnection] = useState<Connection | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Question workflow state
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [theirAnswer, setTheirAnswer] = useState('');
  const [myAnswer, setMyAnswer] = useState('');
  const [saving, setSaving] = useState(false);
  const [loadingQuestion, setLoadingQuestion] = useState(false);
  
  // Usage history state
  const [usageHistory, setUsageHistory] = useState<UsageRecord[]>([]);
  
  // Edit state
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTheirAnswer, setEditTheirAnswer] = useState('');
  const [editMyAnswer, setEditMyAnswer] = useState('');

  useEffect(() => {
    fetchData();
  }, [connectionId, getAuthToken]);

  const fetchData = async () => {
    try {
      // Fetch connection
      const connectionsResponse = await apiClient.get('/connections');
      const connections = connectionsResponse.data;
      const found = connections.find((c: Connection) => c.id === connectionId);
      
      if (!found) {
        setError('Connection not found');
      } else {
        setConnection(found);  
      // Fetch usage history
      const usageResponse = await apiClient.get(`/connections/${connectionId}/usage`);
      const usage = usageResponse.data;
      setUsageHistory(usage);
      }
    } catch (err) {
      setError('Failed to load connection');
    } finally {
      setLoading(false);
    }
  };

  const fetchQuestion = async (category: Category) => {
    setLoadingQuestion(true);
    setError(null);
    try {
      const response = await apiClient.get(`/questions/random?category=${category}&connection_id=${connectionId}`);
      const question = response.data;
      
      setCurrentQuestion(question);
      setTheirAnswer('');
      setMyAnswer('');
    } catch (error: any) {
      if (error.response?.data?.code === 'ALL_QUESTIONS_USED') {
        setError(`You've used all questions in the '${category}' category! Try another category.`);
      } else {
        setError('Failed to load question');
      }
    } finally {
      setLoadingQuestion(false);
    }
  };

  const handleSaveUsage = async () => {
    if (!currentQuestion) return;
    
    setSaving(true);
    setError(null);
    
    try {
      await apiClient.post(`/connections/${connectionId}/usage`, {
        question_id: currentQuestion.id,
        question_text: currentQuestion.text,
        category: currentQuestion.category,
        their_answer: theirAnswer,
        my_answer: myAnswer
      });
      
      // Refresh
      await fetchData();
      
      // Clear form
      setCurrentQuestion(null);
      setTheirAnswer('');
      setMyAnswer('');
    } catch (err) {
      setError('Failed to save usage');
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (record: UsageRecord) => {
    setEditingId(record.usage_id);
    setEditTheirAnswer(record.their_answer);
    setEditMyAnswer(record.my_answer);
  };

  const handleSaveEdit = async (usageId: string) => {
    try {
      await apiClient.put(`/connections/${connectionId}/usage/${usageId}`, {
        their_answer: editTheirAnswer,
        my_answer: editMyAnswer
      });
      
      // Refresh
      await fetchData();
      setEditingId(null);
    } catch (err) {
      alert('Failed to update. Please try again.');
    }
  };

  const handleDeleteUsage = async (usageId: string) => {
    if (!confirm('Delete this conversation record?')) return;
    
    try {
      await apiClient.delete(`/connections/${connectionId}/usage/${usageId}`);
      
      // Refresh
      await fetchData();
    } catch (err) {
      alert('Failed to delete. Please try again.');
    }
  };

  const handleBack = () => navigate('/connections');

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
        </div>
      </div>
    );
  }

  if (error && !connection) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-red-800 mb-2">Error Loading Connection</h2>
          <p className="text-red-600 mb-4">{error}</p>
          <button onClick={handleBack} className="bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600">
            ← Back to Connections
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <button onClick={handleBack} className="flex items-center text-gray-600 hover:text-purple-600 mb-4">
        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Back to Connections
      </button>

      <h1 className="text-3xl font-bold text-gray-800">{connection?.name}</h1>
      <p className="text-gray-500 mt-2">
        Created: {new Date(connection?.created_at || '').toLocaleDateString('en-US', {
          year: 'numeric', month: 'long', day: 'numeric',
        })}
      </p>

      {/* Category Buttons */}
      <div className="mt-8">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">💬 Ask a Question</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {(Object.keys(CATEGORIES) as Category[]).map((category) => {
            const config = CATEGORIES[category];
            return (
              <button
                key={category}
                onClick={() => fetchQuestion(category)}
                disabled={loadingQuestion}
                className={`${config.color} text-white font-semibold py-4 px-3 rounded-xl transform transition-all hover:scale-105 disabled:opacity-50 shadow-lg flex flex-col items-center gap-2`}
              >
                <span className="text-2xl">{config.emoji}</span>
                <span className="text-sm">{config.name}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Question & Answers */}
      {currentQuestion && (
        <div className="mt-6 bg-white rounded-xl shadow-lg p-6">
          <div className="mb-4">
            <span className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-sm font-medium">
              {currentQuestion.category}
            </span>
          </div>
          <p className="text-xl text-gray-800 mb-6">{currentQuestion.text}</p>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                What did {connection?.name} say?
              </label>
              <textarea
                value={theirAnswer}
                onChange={(e) => setTheirAnswer(e.target.value.slice(0, 1000))}
                rows={5}
                maxLength={1000}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                placeholder="Their response..."
              />
              <div className={`text-right text-sm mt-1 ${theirAnswer.length >= 1000 ? 'text-red-600 font-semibold' : 'text-gray-500'}`}>
                {theirAnswer.length >= 1000 && '⚠️ Maximum length reached! '}
                {theirAnswer.length}/1000 characters
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                What did you say?
              </label>
              <textarea
                value={myAnswer}
                onChange={(e) => setMyAnswer(e.target.value.slice(0, 1000))}
                rows={5}
                maxLength={1000}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                placeholder="Your response..."
              />
              <div className={`text-right text-sm mt-1 ${myAnswer.length >= 1000 ? 'text-red-600 font-semibold' : 'text-gray-500'}`}>
                {myAnswer.length >= 1000 && '⚠️ Maximum length reached! '}
                {myAnswer.length}/1000 characters
              </div>
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={() => setCurrentQuestion(null)}
                className="flex-1 px-6 py-3 border border-gray-300 rounded-lg font-medium hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveUsage}
                disabled={saving}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold rounded-lg disabled:opacity-50"
              >
                {saving ? 'Saving...' : '✅ Save'}
              </button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">{error}</p>
        </div>
      )}

      {/* Usage History */}
      <div className="mt-8">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          📝 Conversation History ({usageHistory.length})
        </h2>
        
        {usageHistory.length === 0 ? (
          <div className="bg-gray-50 rounded-lg p-8 text-center">
            <p className="text-gray-500">No questions used yet. Start by selecting a category above!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {usageHistory.map((record) => (

              <div key={record.usage_id} className="bg-white rounded-lg shadow p-6">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex items-center gap-2">
                    {record.category && (
                      <span className={`${CATEGORIES[record.category as Category]?.color.replace('hover:bg', 'bg').split(' ')[0]} text-white px-2 py-1 rounded text-xs font-medium`}>
                        {CATEGORIES[record.category as Category]?.emoji} {CATEGORIES[record.category as Category]?.name || record.category}
                      </span>
                    )}
                    <span className="text-sm text-gray-500">
                      {new Date(record.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEdit(record)}
                      className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                    >
                      ✏️ Edit
                    </button>
                    <button
                      onClick={() => handleDeleteUsage(record.usage_id)}
                      className="text-red-600 hover:text-red-800 text-sm font-medium"
                    >
                      🗑️ Delete
                    </button>
                  </div>
                </div>
                
                <div className="mb-4 p-3 bg-purple-50 rounded-lg">
                  <p className="text-sm font-medium text-purple-700">Question:</p>
                  <p className="text-gray-800 mt-1">{record.question_text}</p>
                </div>

                {editingId === record.usage_id ? (
                  // Edit Mode
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">They said:</label>
                      <textarea
                        value={editTheirAnswer}
                        onChange={(e) => setEditTheirAnswer(e.target.value.slice(0, 1000))}
                        rows={5}
                        maxLength={1000}
                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                      />
                      <div className={`text-right text-sm mt-1 ${editTheirAnswer.length >= 1000 ? 'text-red-600 font-semibold' : 'text-gray-500'}`}>
                        {editTheirAnswer.length >= 1000 && '⚠️ Maximum length reached! '}
                        {editTheirAnswer.length}/1000 characters
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">I said:</label>
                      <textarea
                        value={editMyAnswer}
                        onChange={(e) => setEditMyAnswer(e.target.value.slice(0, 1000))}
                        rows={5}
                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                      />
                      <div className={`text-right text-sm mt-1 ${editMyAnswer.length >= 1000 ? 'text-red-600 font-semibold' : 'text-gray-500'}`}>
                        {editMyAnswer.length >= 1000 && '⚠️ Maximum length reached! '}
                        {editMyAnswer.length}/1000 characters
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setEditingId(null)}
                        className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={() => handleSaveEdit(record.usage_id)}
                        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                      >
                        Save Changes
                      </button>
                    </div>
                  </div>
                ) : (
                  // View Mode
                  <div className="space-y-3 pl-3">
                    <div>
                      <p className="text-sm font-medium text-gray-700">They said:</p>
                      <p className="text-gray-600 mt-1">{record.their_answer || '(no answer recorded)'}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">I said:</p>
                      <p className="text-gray-600 mt-1">{record.my_answer || '(no answer recorded)'}</p>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

