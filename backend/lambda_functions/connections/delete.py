"""
DELETE /connections/{connection_id} Lambda Handler
"""

import json
from typing import Dict, Any, Optional

from shared.responses import success_response, error_response
from shared.dynamodb import table


def get_connection(user_id: str, connection_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific connection to verify ownership."""
    try:
        response = table.get_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'CONNECTION#{connection_id}'
            }
        )
        
        return response.get('Item')
    
    except Exception as e:
        print(f"Error getting connection: {str(e)}")
        return None


def delete_connection(user_id: str, connection_id: str) -> bool:
    """Delete a connection from DynamoDB."""
    try:
        table.delete_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'CONNECTION#{connection_id}'
            }
        )
        return True
    
    except Exception as e:
        print(f"Error deleting connection: {str(e)}")
        raise


def handler(event, context):
    """Lambda handler for DELETE /connections/{connection_id}"""
    
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
                error_code="INVALID_TOKEN",
                event=event
            )
        
        # Get connection_id from path parameters
        path_params = event.get('pathParameters', {})
        connection_id = path_params.get('connection_id')
        
        if not connection_id:
            return error_response(
                "Missing connection_id in path",
                status_code=400,
                error_code="MISSING_CONNECTION_ID",
                event=event
            )
        
        # Verify connection exists and belongs to user
        print(f"Checking if connection {connection_id} exists for user {user_id}")
        connection = get_connection(user_id, connection_id)
        
        if not connection:
            return error_response(
                "Connection not found",
                status_code=404,
                error_code="CONNECTION_NOT_FOUND",
                event=event
            )
        
        # Delete the connection
        print(f"Deleting connection {connection_id} for user {user_id}")
        delete_connection(user_id, connection_id)
        
        # Return success with empty object
        return success_response({"message": "Connection deleted successfully"}, event=event)
    
    except Exception as e:
        print(f"Error in delete handler: {str(e)}")
        return error_response(
            "Internal server error",
            status_code=500,
            error_code="INTERNAL_ERROR",
            event=event
        )