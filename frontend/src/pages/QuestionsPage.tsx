import React, { useState } from 'react';
import apiClient from '../api/client';

interface Question {
  id: string;
  text: string;
  category: string;
}

type Category = 'life' | 'random' | 'deep' | 'experiences';

const CATEGORIES: Record<Category, { name: string; color: string; emoji: string }> = {
  life: { name: 'Life', color: 'bg-blue-500 hover:bg-blue-600', emoji: '🌱' },
  random: { name: 'Random', color: 'bg-purple-500 hover:bg-purple-600', emoji: '🎲' },
  deep: { name: 'Deep', color: 'bg-indigo-500 hover:bg-indigo-600', emoji: '🤔' },
  experiences: { name: 'Experiences', color: 'bg-pink-500 hover:bg-pink-600', emoji: '✨' }
};

const QuestionsPage: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRandomQuestion = async (category: Category) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get(`/questions/random?category=${category}`);
      const question: Question = response.data;
      setCurrentQuestion(question);
      setSelectedCategory(category);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-purple-50 to-blue-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">💬 Conversation Starters</h1>
          <p className="text-lg text-gray-600">Choose a category to get random questions</p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
          {(Object.keys(CATEGORIES) as Category[]).map((category) => {
            const config = CATEGORIES[category];
            return (
              <button
                key={category}
                onClick={() => fetchRandomQuestion(category)}
                disabled={loading}
                className={`${config.color} ${selectedCategory === category ? 'ring-4 ring-offset-2 ring-gray-300' : ''} text-white font-semibold py-6 px-4 rounded-xl transform transition-all hover:scale-105 active:scale-95 disabled:opacity-50 shadow-lg flex flex-col items-center gap-2`}
              >
                <span className="text-3xl">{config.emoji}</span>
                <span className="text-lg">{config.name}</span>
              </button>
            );
          })}
        </div>

        {/* ADD HINT HERE */}
        <div className="text-center mb-8">
          <p className="text-sm text-gray-500">
            💡 Select a connection to start recording answers
          </p>
        </div>

        {currentQuestion && !loading && (
          <div className="bg-white rounded-2xl shadow-2xl p-8 mb-6">
            <div className="flex items-center justify-between mb-6">
              <span className={`${CATEGORIES[selectedCategory!].color.split(' ')[0]} text-white px-4 py-2 rounded-full text-sm`}>
                {CATEGORIES[selectedCategory!].emoji} {CATEGORIES[selectedCategory!].name}
              </span>
              <span className="text-sm text-gray-400">#{currentQuestion.id}</span>
            </div>
            <p className="text-2xl text-gray-800 leading-relaxed mb-8">{currentQuestion.text}</p>
            
            {/* Single Button - Get Another */}
            <button 
              onClick={() => fetchRandomQuestion(selectedCategory!)} 
              disabled={loading}
              className="w-full bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600 text-white font-semibold py-4 px-6 rounded-xl transform transition-all hover:scale-105 shadow-lg"
            >
              🔄 Get Another {CATEGORIES[selectedCategory!].name} Question
            </button>
          </div>
        )}

        {loading && (
          <div className="bg-white rounded-2xl shadow-2xl p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent mb-4"></div>
            <p className="text-gray-600 text-lg">Finding a great question...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-6 text-center">
            <p className="text-red-700 font-medium">{error}</p>
          </div>
        )}

        {!currentQuestion && !loading && !error && (
          <div className="bg-white rounded-2xl shadow-2xl p-12 text-center">
            <span className="text-6xl mb-4 block">💭</span>
            <h3 className="text-2xl font-bold text-gray-800 mb-3">Ready to start a conversation?</h3>
            <p className="text-gray-600 text-lg">Choose a category above!</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default QuestionsPage;
