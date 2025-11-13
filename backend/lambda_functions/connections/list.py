"""
GET /connections Lambda Handler

Returns list of all connections for the authenticated user.
Includes count of questions used with each connection.
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


def get_usage_count(connection_id: str) -> int:
    """
    Get count of usage records for a connection.
    
    Args:
        connection_id: Connection ID
        
    Returns:
        Number of questions used with this connection
    """
    try:
        response = table.query(
            IndexName='GSI1',
            KeyConditionExpression='GSI1PK = :gsi1pk',
            ExpressionAttributeValues={
                ':gsi1pk': f'CONNECTION#{connection_id}'
            },
            Select='COUNT'  # Only count, don't return items
        )
        
        return response.get('Count', 0)
    
    except Exception as e:
        print(f"Error getting usage count: {str(e)}")
        return 0


def clean_connection_for_response(connection: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove DynamoDB internal fields and add usage count.
    """
    connection_id = connection['connection_id']
    usage_count = get_usage_count(connection_id)
    
    return {
        'id': connection_id,
        'name': connection['name'],
        'created_at': connection['created_at'],
        'usage_count': usage_count  # Add question count
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
        
        # Clean and return (with usage counts)
        clean_connections = [clean_connection_for_response(c) for c in connections]
        
        return success_response(clean_connections)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return error_response("Internal server error", status_code=500, error_code="INTERNAL_ERROR")
