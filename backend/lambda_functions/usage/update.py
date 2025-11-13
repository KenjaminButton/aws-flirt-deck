"""
PUT /connections/{connection_id}/usage/{usage_id} Lambda Handler

Updates a usage record (edit answers for a question).
"""

import json
from datetime import datetime

from shared.responses import success_response, error_response
from shared.dynamodb import table


def handler(event, context):
    """Lambda handler for PUT /connections/{connection_id}/usage/{usage_id}"""
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Get user ID from JWT
        authorizer = event.get('requestContext', {}).get('authorizer', {})
        claims = authorizer.get('claims', {})
        user_id = claims.get('sub')
        
        if not user_id:
            return error_response("Unauthorized", 401, "UNAUTHORIZED")
        
        # Get IDs from path
        path_params = event.get('pathParameters', {})
        connection_id = path_params.get('connection_id')
        usage_id = path_params.get('usage_id')
        
        if not connection_id or not usage_id:
            return error_response("Missing parameters", 400, "MISSING_PARAMETER")
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        their_answer = body.get('their_answer', '')
        my_answer = body.get('my_answer', '')
        
        # Verify connection belongs to user
        connection = table.get_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'CONNECTION#{connection_id}'
            }
        ).get('Item')
        
        if not connection:
            return error_response("Connection not found", 404, "NOT_FOUND")
        
        # Update the usage record
        timestamp = datetime.utcnow().isoformat()
        
        response = table.update_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'USAGE#{connection_id}#{usage_id}'
            },
            UpdateExpression='SET their_answer = :their, my_answer = :my, updated_at = :updated',
            ExpressionAttributeValues={
                ':their': their_answer,
                ':my': my_answer,
                ':updated': timestamp
            },
            ReturnValues='ALL_NEW'
        )
        
        updated_item = response.get('Attributes')
        
        # Return clean response
        return success_response({
            'usage_id': updated_item['usage_id'],
            'connection_id': updated_item['connection_id'],
            'question_id': updated_item['question_id'],
            'question_text': updated_item.get('question_text', ''),
            'their_answer': updated_item['their_answer'],
            'my_answer': updated_item['my_answer'],
            'created_at': updated_item['created_at'],
            'updated_at': updated_item.get('updated_at', updated_item['created_at'])
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return error_response("Internal server error", 500, "INTERNAL_ERROR")
