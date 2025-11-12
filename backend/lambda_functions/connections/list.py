"""
GET /connections Lambda Handler

Returns list of all connections for the authenticated user.
"""

import json
from typing import List, Dict, Any

from shared.responses import success_response, error_response
from shared.dynamodb import table


def get_user_connections(user_id: str) -> List[Dict[str, Any]]:
    """
    Get all connections for a user.
    
    Args:
        user_id: Cognito user ID
        
    Returns:
        List of connection objects
    """
    try:
        response = table.query(
            KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
            ExpressionAttributeValues={
                ':pk': f'USER#{user_id}',
                ':sk_prefix': 'CONNECTION#'
            }
        )
        
        return response.get('Items', [])
    
    except Exception as e:
        print(f"Error getting connections: {str(e)}")
        raise


def clean_connection_for_response(connection: Dict[str, Any]) -> Dict[str, Any]:
    """Remove DynamoDB internal fields."""
    return {
        'id': connection['connection_id'],
        'name': connection['name'],
        'created_at': connection['created_at']
    }


def handler(event, context):
    """Lambda handler for GET /connections"""
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Get user ID from JWT
        authorizer = event.get('requestContext', {}).get('authorizer', {})
        claims = authorizer.get('claims', {})
        user_id = claims.get('sub')
        
        if not user_id:
            return error_response(
                "Missing user ID in token",
                status_code=401,
                error_code="INVALID_TOKEN"
            )
        
        # Get connections
        connections = get_user_connections(user_id)
        
        # Clean and return
        clean_connections = [clean_connection_for_response(c) for c in connections]
        
        return success_response(clean_connections)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return error_response("Internal server error", status_code=500, error_code="INTERNAL_ERROR")
