"""
GET /questions/random Lambda Handler

Returns a random conversation starter question from a specified category.
This is the main endpoint for browsing questions in FlirtDeck.

Flow:
1. Extract category from query parameters (?category=life)
2. Validate category is one of: life, random, deep, experiences
3. Query DynamoDB GSI1 for all questions in that category
4. Pick one question randomly
5. Return to frontend

Think of this like a vending machine:
- User presses button (category)
- Machine finds items in that section (GSI query)
- Randomly selects one (random.choice)
- Dispenses it (JSON response)
"""

import json
import sys
import os
import random
from typing import Dict, Any, Optional

# Add shared utilities to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.responses import success_response, error_response
from shared.dynamodb import table

# Valid question categories
# These must match the categories in questions_data.py
VALID_CATEGORIES = ['life', 'random', 'deep', 'experiences']


def get_questions_by_category(category: str) -> list:
    """
    Query all questions in a specific category using GSI1.
    
    This uses the Global Secondary Index we created for efficient
    category-based queries. Much faster than scanning the whole table!
    
    Args:
        category: Question category (life/random/deep/experiences)
    
    Returns:
        List of question items from DynamoDB
        
    Example:
        questions = get_questions_by_category("life")
        # Returns: [{"question_id": "life_001", "text": "...", ...}, ...]
        
    DynamoDB Query:
        Index: GSI1
        Condition: GSI1PK = "CATEGORY#life"
        Result: All questions with that category
    """
    try:
        response = table.query(
            IndexName='GSI1',
            KeyConditionExpression='GSI1PK = :pk',
            ExpressionAttributeValues={
                ':pk': f'CATEGORY#{category}'
            }
        )
        
        return response.get('Items', [])
    
    except Exception as e:
        print(f"Error querying category '{category}': {str(e)}")
        raise


def clean_question_for_response(question: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove DynamoDB internal fields before sending to frontend.
    
    Frontend doesn't need to see PK, SK, GSI keys, etc.
    Only send the data they actually need.
    
    Args:
        question: Raw DynamoDB item
        
    Returns:
        Cleaned question dict with only user-facing fields
        
    Example:
        Input:  {"PK": "QUESTION#life_001", "SK": "METADATA", "text": "...", ...}
        Output: {"id": "life_001", "text": "...", "category": "life"}
    """
    return {
        'id': question['question_id'],
        'text': question['text'],
        'category': question['category']
    }


def handler(event, context):
    """
    Lambda handler for GET /questions/random endpoint
    
    Query Parameters:
        category (required): life, random, deep, or experiences
    
    Response:
        200: {"id": "life_001", "text": "...", "category": "life"}
        400: {"error": "Invalid category"}
        404: {"error": "No questions found in this category"}
        500: {"error": "Internal server error"}
    
    Example Request:
        GET /questions/random?category=life
        
    Example Response:
        {
            "id": "life_002",
            "text": "What's one thing you'd change about your daily routine?",
            "category": "life"
        }
    """
    
    # Log incoming request for debugging
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract query parameters from API Gateway event
        # API Gateway puts query params in event['queryStringParameters']
        query_params = event.get('queryStringParameters') or {}
        category = query_params.get('category')
        
        # Validate: category parameter is required
        if not category:
            return error_response(
                "Missing 'category' query parameter. Use: ?category=life",
                status_code=400,
                error_code="MISSING_CATEGORY"
            )
        
        # Validate: category must be one of the valid options
        if category not in VALID_CATEGORIES:
            return error_response(
                f"Invalid category '{category}'. Must be one of: {', '.join(VALID_CATEGORIES)}",
                status_code=400,
                error_code="INVALID_CATEGORY"
            )
        
        # Query DynamoDB for all questions in this category
        print(f"Querying questions for category: {category}")
        questions = get_questions_by_category(category)
        
        # Handle case where category has no questions
        # This shouldn't happen with our seed data, but good to check!
        if not questions:
            return error_response(
                f"No questions found in category '{category}'",
                status_code=404,
                error_code="NO_QUESTIONS_FOUND"
            )
        
        # Pick a random question from the results
        # This is the "magic" - different question each time!
        random_question = random.choice(questions)
        print(f"Selected question: {random_question['question_id']}")
        
        # Clean up the question before sending to frontend
        # Remove DynamoDB internal fields (PK, SK, GSI keys)
        clean_question = clean_question_for_response(random_question)
        
        # Return success response
        return success_response(clean_question)
    
    except Exception as e:
        # Log error for CloudWatch debugging
        print(f"Error in get_random handler: {str(e)}")
        
        # Return generic error to user (don't expose internal details)
        return error_response(
            "Internal server error",
            status_code=500,
            error_code="INTERNAL_ERROR"
        )