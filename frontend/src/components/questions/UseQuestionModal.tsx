/**
 * Use Question Modal Component
 * 
 * Modal for recording that a question was used with a connection.
 * User selects connection and enters both answers.
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import apiClient from '../../api/client';

interface Connection {
  id: string;
  name: string;
}

interface UseQuestionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  questionId: string;
  questionText: string;
}

const UseQuestionModal: React.FC<UseQuestionModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  questionId,
  questionText
}) => {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [selectedConnectionId, setSelectedConnectionId] = useState('');
  const [theirAnswer, setTheirAnswer] = useState('');
  const [myAnswer, setMyAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch connections when modal opens
  useEffect(() => {
    if (isOpen) {
      fetchConnections();
    }
  }, [isOpen]);

  const fetchConnections = async () => {
    try {
      const response = await apiClient.get('/connections');
      setConnections(response.data);
    } catch (err) {
      setError('Failed to load connections');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedConnectionId) {
      setError('Please select a connection');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await apiClient.post(`/connections/${selectedConnectionId}/usage`, {
        question_id: questionId,
        their_answer: theirAnswer,
        my_answer: myAnswer
      });

      // Success!
      onSuccess();
      handleClose();
    } catch (err) {
      setError('Failed to save. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setSelectedConnectionId('');
    setTheirAnswer('');
    setMyAnswer('');
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                📝 Record Question Usage
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                Who did you use this question with?
              </p>
            </div>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Question Display */}
          <div className="bg-purple-50 rounded-lg p-4 mb-6">
            <p className="text-sm text-purple-600 font-medium mb-1">Question:</p>
            <p className="text-gray-800">{questionText}</p>
          </div>

          <form onSubmit={handleSubmit}>
            {/* Select Connection */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Connection *
              </label>
              <select
                value={selectedConnectionId}
                onChange={(e) => setSelectedConnectionId(e.target.value)}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="">Choose a connection...</option>
                {connections.map((conn) => (
                  <option key={conn.id} value={conn.id}>
                    {conn.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Their Answer */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                What did they say?
              </label>
              <textarea
                value={theirAnswer}
                onChange={(e) => setTheirAnswer(e.target.value)}
                rows={3}
                placeholder="Their response..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              />
            </div>

            {/* My Answer */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                What did you say?
              </label>
              <textarea
                value={myAnswer}
                onChange={(e) => setMyAnswer(e.target.value)}
                rows={3}
                placeholder="Your response..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              />
            </div>

            {/* Error */}
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}

            {/* Buttons */}
            <div className="flex gap-3">
              <button
                type="button"
                onClick={handleClose}
                className="flex-1 px-6 py-3 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold rounded-lg disabled:opacity-50"
              >
                {loading ? 'Saving...' : '✅ Save Usage'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default UseQuestionModal;
