"""
POST /connections Lambda Handler
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any

from shared.responses import success_response, error_response
from shared.dynamodb import table


def get_user_subscription_status(user_id: str) -> str:
    """Get user's subscription status from their profile."""
    try:
        response = table.get_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': 'PROFILE'
            }
        )
        
        item = response.get('Item')
        if not item:
            return 'free'
        
        return item.get('subscription_status', 'free')
    
    except Exception as e:
        print(f"Error getting subscription status: {str(e)}")
        return 'free'


def count_user_connections(user_id: str) -> int:
    """Count how many connections a user has."""
    try:
        response = table.query(
            KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
            ExpressionAttributeValues={
                ':pk': f'USER#{user_id}',
                ':sk_prefix': 'CONNECTION#'
            }
        )
        
        return response.get('Count', 0)
    
    except Exception as e:
        print(f"Error counting connections: {str(e)}")
        return 0


def create_connection(user_id: str, name: str) -> Dict[str, Any]:
    """Create a new connection in DynamoDB."""
    connection_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    connection = {
        'PK': f'USER#{user_id}',
        'SK': f'CONNECTION#{connection_id}',
        'connection_id': connection_id,
        'name': name,
        'created_at': timestamp,
        'updated_at': timestamp,
        
        'GSI1PK': f'USER#{user_id}',
        'GSI1SK': f'CONNECTION#{timestamp}'
    }
    
    try:
        table.put_item(Item=connection)
        return connection
    
    except Exception as e:
        print(f"Error creating connection: {str(e)}")
        raise


def clean_connection_for_response(connection: Dict[str, Any]) -> Dict[str, Any]:
    """Remove DynamoDB internal fields before sending to frontend."""
    return {
        'id': connection['connection_id'],
        'name': connection['name'],
        'created_at': connection['created_at']
    }


def handler(event, context):
    """Lambda handler for POST /connections endpoint"""
    
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract user ID from Cognito authorizer
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
        
        # Parse request body
        try:
            body = json.loads(event.get('body', '{}'))
        except json.JSONDecodeError:
            return error_response(
                "Invalid JSON in request body",
                status_code=400,
                error_code="INVALID_JSON",
                event=event
            )
        
        name = body.get('name', '').strip()
        
        # Validate name
        if not name:
            return error_response(
                "Missing 'name' field",
                status_code=400,
                error_code="MISSING_NAME",
                event=event
            )
        
        if len(name) > 100:
            return error_response(
                "Name too long (max 100 characters)",
                status_code=400,
                error_code="NAME_TOO_LONG",
                event=event
            )
        
        # Check subscription status
        print(f"Checking subscription status for user: {user_id}")
        subscription_status = get_user_subscription_status(user_id)
        
        # If free tier, check connection limit
        if subscription_status == 'free':
            print("User is on free tier, checking connection limit")
            connection_count = count_user_connections(user_id)
            print(f"User has {connection_count} connections")
            
            # Free tier limit: 1 connection
            if connection_count >= 1:
                return error_response(
                    "Free tier limit reached. Upgrade to Premium for unlimited connections.",
                    status_code=403,
                    error_code="FREE_TIER_LIMIT",
                    event=event
                )
        
        # Create connection
        print(f"Creating connection for user {user_id}: {name}")
        connection = create_connection(user_id, name)
        
        # Clean and return
        clean_connection = clean_connection_for_response(connection)
        
        return success_response(clean_connection, status_code=201, event=event)
    
    except Exception as e:
        print(f"Error in create handler: {str(e)}")
        return error_response(
            "Internal server error",
            status_code=500,
            error_code="INTERNAL_ERROR",
            event=event
        )