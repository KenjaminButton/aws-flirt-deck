/**
 * Questions Page Component
 * 
 * Purpose:
 * Main page for browsing conversation starter questions by category.
 * Users can click category buttons to get random questions from that category.
 * 
 * Features:
 * - 4 category buttons: Life, Random, Deep, Experiences
 * - Display random question from selected category
 * - "Get Another" button to fetch new question from same category
 * - Loading states and error handling
 * - Beautiful UI with Tailwind CSS
 * 
 * Flow:
 * 1. User clicks category button (e.g., "Life")
 * 2. API call to GET /questions/random?category=life
 * 3. Display returned question
 * 4. User clicks "Get Another" → Fetch new random question from same category
 * 
 * Think of this like a question vending machine:
 * - Press category button → Machine section lights up
 * - Question dispenses → Display on screen
 * - Want another? → Press "Get Another" button
 */

import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

// Type definitions for type safety
interface Question {
  id: string;
  text: string;
  category: string;
}

// Category type ensures we only use valid categories
type Category = 'life' | 'random' | 'deep' | 'experiences';

// Category configuration with display names, colors, and descriptions
const CATEGORIES: Record<Category, { name: string; color: string; description: string; emoji: string }> = {
  life: {
    name: 'Life',
    color: 'bg-blue-500 hover:bg-blue-600',
    description: 'Personal growth & lifestyle',
    emoji: '🌱'
  },
  random: {
    name: 'Random',
    color: 'bg-purple-500 hover:bg-purple-600',
    description: 'Fun & lighthearted',
    emoji: '🎲'
  },
  deep: {
    name: 'Deep',
    color: 'bg-indigo-500 hover:bg-indigo-600',
    description: 'Philosophical & meaningful',
    emoji: '🤔'
  },
  experiences: {
    name: 'Experiences',
    color: 'bg-pink-500 hover:bg-pink-600',
    description: 'Stories & adventures',
    emoji: '✨'
  }
};

const QuestionsPage: React.FC = () => {
  // Get authentication context for API calls
  const { getAuthToken } = useAuth();
  
  // Component state
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch a random question from the specified category
   * Makes authenticated API call to GET /questions/random
   */
  const fetchRandomQuestion = async (category: Category) => {
    setLoading(true);
    setError(null);

    try {
      // Get authentication token from Cognito
      const token = await getAuthToken();
      
      // Get API URL from environment variables
      const apiUrl = import.meta.env.VITE_API_URL;
      
      // Make API request with authentication
      const response = await fetch(
        `${apiUrl}/questions/random?category=${category}`,
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      // Handle HTTP errors
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch question');
      }

      // Parse and set the question
      const question: Question = await response.json();
      setCurrentQuestion(question);
      setSelectedCategory(category);
      
    } catch (err) {
      console.error('Error fetching question:', err);
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle category button click
   * Fetches a random question from the selected category
   */
  const handleCategoryClick = (category: Category) => {
    fetchRandomQuestion(category);
  };

  /**
   * Handle "Get Another" button click
   * Fetches another random question from the currently selected category
   */
  const handleGetAnother = () => {
    if (selectedCategory) {
      fetchRandomQuestion(selectedCategory);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-purple-50 to-blue-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Page Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            💬 Conversation Starters
          </h1>
          <p className="text-lg text-gray-600">
            Choose a category to get random questions
          </p>
        </div>

        {/* Category Buttons Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
          {(Object.keys(CATEGORIES) as Category[]).map((category) => {
            const config = CATEGORIES[category];
            const isSelected = selectedCategory === category;
            
            return (
              <button
                key={category}
                onClick={() => handleCategoryClick(category)}
                disabled={loading}
                className={`
                  ${config.color}
                  ${isSelected ? 'ring-4 ring-offset-2 ring-gray-300' : ''}
                  text-white font-semibold py-6 px-4 rounded-xl
                  transform transition-all duration-200
                  hover:scale-105 active:scale-95
                  disabled:opacity-50 disabled:cursor-not-allowed
                  shadow-lg hover:shadow-xl
                  flex flex-col items-center gap-2
                `}
              >
                <span className="text-3xl">{config.emoji}</span>
                <span className="text-lg">{config.name}</span>
                <span className="text-xs opacity-80">{config.description}</span>
              </button>
            );
          })}
        </div>

        {/* Question Display Card */}
        {currentQuestion && !loading && (
          <div className="bg-white rounded-2xl shadow-2xl p-8 mb-6 transform transition-all duration-300 animate-fadeIn">
            {/* Category Badge */}
            <div className="flex items-center justify-between mb-6">
              <span className={`
                ${CATEGORIES[selectedCategory!].color.split(' ')[0]} 
                text-white px-4 py-2 rounded-full text-sm font-medium
              `}>
                {CATEGORIES[selectedCategory!].emoji} {CATEGORIES[selectedCategory!].name}
              </span>
              <span className="text-sm text-gray-400">#{currentQuestion.id}</span>
            </div>

            {/* Question Text */}
            <p className="text-2xl text-gray-800 leading-relaxed mb-8 font-medium">
              {currentQuestion.text}
            </p>

            {/* Get Another Button */}
            <button
              onClick={handleGetAnother}
              disabled={loading}
              className="
                w-full bg-gradient-to-r from-pink-500 to-purple-500
                hover:from-pink-600 hover:to-purple-600
                text-white font-semibold py-4 px-6 rounded-xl
                transform transition-all duration-200
                hover:scale-105 active:scale-95
                disabled:opacity-50 disabled:cursor-not-allowed
                shadow-lg hover:shadow-xl
              "
            >
              🔄 Get Another {CATEGORIES[selectedCategory!].name} Question
            </button>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-2xl shadow-2xl p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent mb-4"></div>
            <p className="text-gray-600 text-lg">Finding a great question...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-6 text-center">
            <span className="text-4xl mb-3 block">⚠️</span>
            <p className="text-red-700 font-medium mb-2">Oops! Something went wrong</p>
            <p className="text-red-600 text-sm">{error}</p>
            <button
              onClick={() => selectedCategory && fetchRandomQuestion(selectedCategory)}
              className="mt-4 bg-red-500 hover:bg-red-600 text-white font-medium py-2 px-6 rounded-lg transition-colors"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Empty State - Show when no category selected */}
        {!currentQuestion && !loading && !error && (
          <div className="bg-white rounded-2xl shadow-2xl p-12 text-center">
            <span className="text-6xl mb-4 block">💭</span>
            <h3 className="text-2xl font-bold text-gray-800 mb-3">
              Ready to start a conversation?
            </h3>
            <p className="text-gray-600 text-lg">
              Choose a category above to get your first question!
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default QuestionsPage;
