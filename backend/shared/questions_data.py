"""
FlirtDeck Questions Database - TEST DATASET

This file contains the master list of conversation starter questions.
Currently contains 12 test questions (3 per category) for initial testing.

Purpose:
- Provides structured question data for seeding DynamoDB
- Each question has: text, category, and unique ID
- Will be expanded to 250+ questions in future update

Categories:
- life: Personal growth, goals, lifestyle
- random: Fun, lighthearted, quirky topics  
- deep: Philosophical, meaningful conversations
- experiences: Stories, memories, adventures

Usage:
    from shared.questions_data import QUESTIONS
    for q in QUESTIONS:
        print(q['text'])
"""

from typing import List, Dict

# Master questions list
# Think of this as our question bank - each question is a conversation spark!
QUESTIONS: List[Dict[str, str]] = [
    # ==================== LIFE CATEGORY ====================
    # Questions about personal growth, goals, and lifestyle choices
    {
        "id": "life_001",
        "text": "If you could master any skill instantly, what would it be and why?",
        "category": "life"
    },
    {
        "id": "life_002", 
        "text": "What's one thing you'd change about your daily routine if you could?",
        "category": "life"
    },
    {
        "id": "life_003",
        "text": "What does a perfect weekend look like to you?",
        "category": "life"
    },
    
    # ==================== RANDOM CATEGORY ====================
    # Fun, lighthearted questions to break the ice
    {
        "id": "random_001",
        "text": "Pineapple on pizza - love it or hate it?",
        "category": "random"
    },
    {
        "id": "random_002",
        "text": "If you could be any animal for a day, what would you choose?",
        "category": "random"
    },
    {
        "id": "random_003",
        "text": "What's the weirdest food combination you actually enjoy?",
        "category": "random"
    },
    
    # ==================== DEEP CATEGORY ====================
    # Philosophical and meaningful conversation starters
    {
        "id": "deep_001",
        "text": "What's a belief you held strongly but later changed your mind about?",
        "category": "deep"
    },
    {
        "id": "deep_002",
        "text": "If you could have dinner with anyone from history, who would it be and what would you ask them?",
        "category": "deep"
    },
    {
        "id": "deep_003",
        "text": "What do you think is the meaning of a life well-lived?",
        "category": "deep"
    },
    
    # ==================== EXPERIENCES CATEGORY ====================
    # Questions about stories, memories, and adventures
    {
        "id": "experiences_001",
        "text": "What's the most spontaneous thing you've ever done?",
        "category": "experiences"
    },
    {
        "id": "experiences_002",
        "text": "Tell me about a moment when you felt completely alive.",
        "category": "experiences"
    },
    {
        "id": "experiences_003",
        "text": "What's a travel destination that exceeded your expectations?",
        "category": "experiences"
    }
]

# Quick stats for verification
QUESTION_COUNT = len(QUESTIONS)
CATEGORIES = list(set(q["category"] for q in QUESTIONS))

# Validation function - makes sure our data is clean
def validate_questions() -> bool:
    """
    Validates the questions data structure.
    
    Returns:
        True if all questions are valid, False otherwise
    
    Checks:
    - Each question has required fields (id, text, category)
    - IDs are unique
    - Categories match expected values
    """
    seen_ids = set()
    valid_categories = {"life", "random", "deep", "experiences"}
    
    for question in QUESTIONS:
        # Check required fields exist
        if not all(key in question for key in ["id", "text", "category"]):
            print(f"❌ Question missing required fields: {question}")
            return False
        
        # Check for duplicate IDs
        if question["id"] in seen_ids:
            print(f"❌ Duplicate question ID found: {question['id']}")
            return False
        seen_ids.add(question["id"])
        
        # Check category is valid
        if question["category"] not in valid_categories:
            print(f"❌ Invalid category '{question['category']}' for question: {question['id']}")
            return False
    
    print(f"✅ All {QUESTION_COUNT} questions validated successfully!")
    print(f"📊 Categories: {', '.join(sorted(CATEGORIES))}")
    return True


if __name__ == "__main__":
    # Run validation when file is executed directly
    # Usage: python questions_data.py
    print("🔍 Validating questions dataset...")
    validate_questions()
    print(f"\n📚 Total questions: {QUESTION_COUNT}")
    for category in sorted(CATEGORIES):
        count = sum(1 for q in QUESTIONS if q["category"] == category)
        print(f"   - {category}: {count} questions")
