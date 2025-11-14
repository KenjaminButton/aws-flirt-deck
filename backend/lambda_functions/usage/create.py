"""
POST /connections/{connection_id}/usage Lambda Handler

Records when a user uses a question with a connection.
Stores both their answer and your answer.

Flow:
1. Get user_id from JWT token
2. Get connection_id from path
3. Get question_id, their_answer, my_answer from body
4. Validate connection belongs to user
5. Create usage record in DynamoDB
6. Return usage object
"""

import json
import sys
import os
from datetime import datetime
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.responses import success_response, error_response
from shared.dynamodb import table

def handler(event, context):
    """
    Lambda handler for POST /connections/{connection_id}/usage
    """
    
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Get user from JWT
        authorizer = event.get('requestContext', {}).get('authorizer', {})
        claims = authorizer.get('claims', {})
        user_id = claims.get('sub')
        
        if not user_id:
            return error_response("Unauthorized", 401, "UNAUTHORIZED")
        
        # Get connection_id from path
        path_params = event.get('pathParameters', {})
        connection_id = path_params.get('connection_id')
        
        if not connection_id:
            return error_response("Missing connection_id", 400, "MISSING_PARAMETER")
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        question_id = body.get('question_id')
        their_answer = body.get('their_answer', '')
        my_answer = body.get('my_answer', '')
        
        # Validate answer lengths
        if len(their_answer) > 1000:
            return error_response("Their answer exceeds 1000 characters", 400, "ANSWER_TOO_LONG")
        if len(my_answer) > 1000:
            return error_response("My answer exceeds 1000 characters", 400, "ANSWER_TOO_LONG")

        # Validate required fields
        if not question_id:
            return error_response("Missing question_id", 400, "MISSING_FIELD")
        
        # Verify connection exists and belongs to user
        connection = table.get_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': f'CONNECTION#{connection_id}'
            }
        ).get('Item')
        
        if not connection:
            return error_response("Connection not found", 404, "NOT_FOUND")
        
        # Create usage record
        timestamp = datetime.utcnow().isoformat()
        usage_id = str(uuid.uuid4())
        
        usage_record = {
            'PK': f'USER#{user_id}',
            'SK': f'USAGE#{connection_id}#{usage_id}',
            'usage_id': usage_id,
            'connection_id': connection_id,
            'question_id': question_id,
            'question_text': body.get('question_text', ''),
            'category': body.get('category', 'unknown'), 
            'their_answer': their_answer,
            'my_answer': my_answer,
            'created_at': timestamp,
            
            # GSI for querying usage by connection
            'GSI1PK': f'CONNECTION#{connection_id}',
            'GSI1SK': f'USAGE#{timestamp}'
        }
        
        table.put_item(Item=usage_record)
        
        # Return clean response (remove DynamoDB keys)
        response_data = {
            'usage_id': usage_id,
            'connection_id': connection_id,
            'question_id': question_id,
            'category': body.get('category', 'unknown'),
            'their_answer': their_answer,
            'my_answer': my_answer,
            'created_at': timestamp
        }
        
        return success_response(response_data, 201)
    
    except Exception as e:
        print(f"Error creating usage: {str(e)}")
        return error_response("Internal server error", 500, "INTERNAL_ERROR")
