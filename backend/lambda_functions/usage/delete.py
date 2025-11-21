"""
DELETE /connections/{connection_id}/usage/{usage_id} Lambda Handler

Deletes a usage record (removes a question/answer from history).
"""

import json

from shared.responses import success_response, error_response
from shared.dynamodb import table


def handler(event, context):
    """Lambda handler for DELETE /connections/{connection_id}/usage/{usage_id}"""
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Get user ID from JWT
        authorizer = event.get('requestContext', {}).get('authorizer', {})
        claims = authorizer.get('claims', {})
        user_id = claims.get('sub')
        
        if not user_id:
            return error_response("Unauthorized", 401, "UNAUTHORIZED", event=event)
        
        # Get IDs from path
        path_params = event.get('pathParameters', {})
        connection_id = path_params.get('connection_id')
        usage_id = path_params.get('usage_id')
        
        if not connection_id or not usage_id:
            return error_response("Missing parameters", 400, "MISSING_PARAMETER", event=event)
        
        # Verify connection belongs to user
        connection = table.get_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'CONNECTION#{connection_id}'
            }
        ).get('Item')
        
        if not connection:
            return error_response("Connection not found", 404, "NOT_FOUND", event=event)
        
        # Delete the usage record
        table.delete_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'USAGE#{connection_id}#{usage_id}'
            }
        )
        
        return success_response({"message": "Usage deleted successfully"}, event=event)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return error_response("Internal server error", 500, "INTERNAL_ERROR", event=event)