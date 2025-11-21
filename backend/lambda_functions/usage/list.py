"""
GET /connections/{connection_id}/usage Lambda Handler

Returns all question usage records for a specific connection.
Shows conversation history (all questions used with this connection).
"""

import json
from typing import List, Dict, Any

from shared.responses import success_response, error_response
from shared.dynamodb import table


def get_connection_usage(user_id: str, connection_id: str) -> List[Dict[str, Any]]:
    """
    Get all usage records for a connection.
    
    Uses GSI1 to query by connection efficiently.
    """
    try:
        response = table.query(
            IndexName='GSI1',
            KeyConditionExpression='GSI1PK = :gsi1pk',
            ExpressionAttributeValues={
                ':gsi1pk': f'CONNECTION#{connection_id}'
            },
            ScanIndexForward=False  # Most recent first
        )
        
        return response.get('Items', [])
    
    except Exception as e:
        print(f"Error getting usage records: {str(e)}")
        raise


def clean_usage_for_response(usage: Dict[str, Any]) -> Dict[str, Any]:
    """Remove DynamoDB internal fields."""
    return {
        'usage_id': usage['usage_id'],
        'connection_id': usage['connection_id'],
        'question_id': usage['question_id'],
        'question_text': usage.get('question_text', ''),
        'category': usage.get('category', 'unknown'), 
        'their_answer': usage.get('their_answer', ''),
        'my_answer': usage.get('my_answer', ''),
        'created_at': usage['created_at']
    }


def handler(event, context):
    """Lambda handler for GET /connections/{connection_id}/usage"""
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Get user ID from JWT
        authorizer = event.get('requestContext', {}).get('authorizer', {})
        claims = authorizer.get('claims', {})
        user_id = claims.get('sub')
        
        if not user_id:
            return error_response("Unauthorized", 401, "UNAUTHORIZED", event=event)
        
        # Get connection_id from path
        path_params = event.get('pathParameters', {})
        connection_id = path_params.get('connection_id')
        
        if not connection_id:
            return error_response("Missing connection_id", 400, "MISSING_PARAMETER", event=event)
        
        # Verify connection belongs to user
        connection = table.get_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'CONNECTION#{connection_id}'
            }
        ).get('Item')
        
        if not connection:
            return error_response("Connection not found", 404, "NOT_FOUND", event=event)
        
        # Get all usage records for this connection
        usage_records = get_connection_usage(user_id, connection_id)
        
        # Clean and return
        clean_records = [clean_usage_for_response(u) for u in usage_records]
        
        return success_response(clean_records, event=event)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return error_response("Internal server error", 500, "INTERNAL_ERROR", event=event)