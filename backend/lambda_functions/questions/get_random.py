"""
GET /questions/random Lambda Handler

Returns a random conversation starter question from a specified category.
"""

import json
import random
from typing import Dict, Any

from shared.responses import success_response, error_response
from shared.dynamodb import table

VALID_CATEGORIES = ['life', 'random', 'deep', 'experiences']


def get_used_question_ids(user_id: str, connection_id: str) -> list:
    """Get list of question IDs already used with this connection."""
    try:
        response = table.query(
            KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
            ExpressionAttributeValues={
                ':pk': f'USER#{user_id}',
                ':sk': f'USAGE#{connection_id}#'
            }
        )
        return [item['question_id'] for item in response.get('Items', [])]
    except Exception as e:
        print(f"Error getting used questions: {str(e)}")
        return []  # If error, return empty (fail open)


def get_questions_by_category(category: str) -> list:
    """Query all questions in a category using GSI1."""
    try:
        response = table.query(
            IndexName='GSI1',
            KeyConditionExpression='GSI1PK = :pk',
            ExpressionAttributeValues={':pk': f'CATEGORY#{category}'}
        )
        return response.get('Items', [])
    except Exception as e:
        print(f"Error querying category '{category}': {str(e)}")
        raise


def clean_question_for_response(question: Dict[str, Any]) -> Dict[str, Any]:
    """Remove DynamoDB internal fields."""
    return {
        'id': question['question_id'],
        'text': question['text'],
        'category': question['category']
    }


def handler(event, context):
    """Lambda handler for GET /questions/random"""
    print(f"Received event: {json.dumps(event)}")
    
    try:
        query_params = event.get('queryStringParameters') or {}
        category = query_params.get('category')
        connection_id = query_params.get('connection_id')  # NEW: Optional parameter
        
        if not category:
            return error_response(
                "Missing 'category' query parameter",
                status_code=400,
                error_code="MISSING_CATEGORY"
            )
        
        if category not in VALID_CATEGORIES:
            return error_response(
                f"Invalid category '{category}'. Must be one of: {', '.join(VALID_CATEGORIES)}",
                status_code=400,
                error_code="INVALID_CATEGORY"
            )
        
        # Get all questions in category
        questions = get_questions_by_category(category)
        
        if not questions:
            return error_response(
                f"No questions found in category '{category}'",
                status_code=404,
                error_code="NO_QUESTIONS_FOUND"
            )
        
        # NEW: If connection_id provided, filter out already-used questions
        if connection_id:
            # Get user ID from JWT
            authorizer = event.get('requestContext', {}).get('authorizer', {})
            claims = authorizer.get('claims', {})
            user_id = claims.get('sub')
            
            if user_id:
                used_ids = get_used_question_ids(user_id, connection_id)
                print(f"Found {len(used_ids)} used questions for connection {connection_id}")
                
                # Filter out used questions
                questions = [q for q in questions if q['question_id'] not in used_ids]
                
                if not questions:
                    return error_response(
                        f"All questions in '{category}' category have been used!",
                        status_code=404,
                        error_code="ALL_QUESTIONS_USED"
                    )
        
        # Pick random from available questions
        random_question = random.choice(questions)
        print(f"Selected question: {random_question['question_id']}")
        
        clean_question = clean_question_for_response(random_question)
        return success_response(clean_question)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return error_response("Internal server error", status_code=500, error_code="INTERNAL_ERROR")
