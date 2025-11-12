"""
POST /connections Lambda Handler

Creates a new connection (conversation partner) for the user.
Enforces free tier limit: free users can only have 1 connection.

Flow:
1. Extract name from request body
2. Get user_id from JWT token (via authorizer)
3. Check subscription status from DynamoDB
4. If free tier: count existing connections
5. If at limit: return 403 error (paywall)
6. Create connection in DynamoDB
7. Return connection object

Think of this like a contact list:
- Free users: 1 contact max
- Premium users: unlimited contacts
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any

from shared.responses import success_response, error_response
from shared.dynamodb import table


def get_user_subscription_status(user_id: str) -> str:
    """
    Get user's subscription status from their profile.
    
    Args:
        user_id: Cognito user ID
        
    Returns:
        Subscription status: 'free' or 'premium'
    """
    try:
        response = table.get_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': 'PROFILE'
            }
        )
        
        item = response.get('Item')
        if not item:
            return 'free'  # Default to free if profile doesn't exist
        
        return item.get('subscription_status', 'free')
    
    except Exception as e:
        print(f"Error getting subscription status: {str(e)}")
        return 'free'  # Fail closed - default to free


def count_user_connections(user_id: str) -> int:
    """
    Count how many connections a user has.
    
    Args:
        user_id: Cognito user ID
        
    Returns:
        Number of connections
        
    Query pattern:
        PK = USER#{user_id}
        SK begins_with CONNECTION#
    """
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
    """
    Create a new connection in DynamoDB.
    
    Args:
        user_id: Cognito user ID
        name: Connection name (e.g., "Sarah from Hinge")
        
    Returns:
        Created connection object
        
    DynamoDB item structure:
        PK: USER#{user_id}
        SK: CONNECTION#{connection_id}
        connection_id: UUID
        name: Connection name
        created_at: ISO timestamp
    """
    connection_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    connection = {
        'PK': f'USER#{user_id}',
        'SK': f'CONNECTION#{connection_id}',
        'connection_id': connection_id,
        'name': name,
        'created_at': timestamp,
        'updated_at': timestamp,
        
        # GSI1 for querying all connections by user
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
    """
    Remove DynamoDB internal fields before sending to frontend.
    
    Args:
        connection: Raw DynamoDB item
        
    Returns:
        Cleaned connection object
    """
    return {
        'id': connection['connection_id'],
        'name': connection['name'],
        'created_at': connection['created_at']
    }


def handler(event, context):
    """
    Lambda handler for POST /connections endpoint
    
    Request Body:
        {
            "name": "Sarah from Hinge"
        }
    
    Response:
        201: {"id": "uuid", "name": "Sarah from Hinge", "created_at": "2024-01-15"}
        400: {"error": "Missing name"}
        403: {"error": "Free tier limit reached. Upgrade to Premium."}
        500: {"error": "Internal server error"}
    """
    
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
                error_code="INVALID_TOKEN"
            )
        
        # Parse request body
        try:
            body = json.loads(event.get('body', '{}'))
        except json.JSONDecodeError:
            return error_response(
                "Invalid JSON in request body",
                status_code=400,
                error_code="INVALID_JSON"
            )
        
        name = body.get('name', '').strip()
        
        # Validate name
        if not name:
            return error_response(
                "Missing 'name' field",
                status_code=400,
                error_code="MISSING_NAME"
            )
        
        if len(name) > 100:
            return error_response(
                "Name too long (max 100 characters)",
                status_code=400,
                error_code="NAME_TOO_LONG"
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
                    error_code="FREE_TIER_LIMIT"
                )
        
        # Create connection
        print(f"Creating connection for user {user_id}: {name}")
        connection = create_connection(user_id, name)
        
        # Clean and return
        clean_connection = clean_connection_for_response(connection)
        
        return success_response(clean_connection, status_code=201)
    
    except Exception as e:
        print(f"Error in create handler: {str(e)}")
        return error_response(
            "Internal server error",
            status_code=500,
            error_code="INTERNAL_ERROR"
        )