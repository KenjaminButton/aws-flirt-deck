"""
GET /auth/me Lambda Handler

Returns the authenticated user's profile.
This is called after Google OAuth login to fetch/create user data.

Flow:
1. API Gateway validates JWT token and passes user info
2. Extract user ID from Cognito claims
3. Check if user exists in DynamoDB
4. If first login, create user profile
5. Return user data to frontend
"""

import json
import sys
import os

# Add shared utilities to Python path
# Lambda needs this to import from shared/ folder
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.responses import success_response, error_response
from shared.dynamodb import get_user_profile, create_user_profile


def handler(event, context):
    """
    Lambda handler for GET /auth/me endpoint
    
    Args:
        event: API Gateway event (contains request data)
        context: Lambda context (runtime info)
    
    Returns:
        API Gateway formatted response
    """
    
    # Log the incoming request for debugging
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract user info from Cognito authorizer
        # API Gateway puts this in event['requestContext']['authorizer']['claims']
        authorizer = event.get('requestContext', {}).get('authorizer', {})
        claims = authorizer.get('claims', {})
        
        # Get user ID (sub = subject, unique user identifier from Cognito)
        user_id = claims.get('sub')
        email = claims.get('email')
        name = claims.get('name')
        
        # Validate that we have required fields
        if not user_id:
            return error_response(
                "Missing user ID in token",
                status_code=401,
                error_code="INVALID_TOKEN"
            )
        
        if not email:
            return error_response(
                "Missing email in token",
                status_code=401,
                error_code="INVALID_TOKEN"
            )
        
        # Check if user profile exists
        profile = get_user_profile(user_id)
        
        # If profile doesn't exist, this is first login - create it
        if not profile:
            print(f"First login for user {user_id}, creating profile")
            profile = create_user_profile(
                user_id=user_id,
                email=email,
                name=name
            )
        
        # Remove DynamoDB-specific fields before returning to frontend
        # Frontend doesn't need to see PK, SK, GSI keys
        clean_profile = {
            'user_id': profile['user_id'],
            'email': profile['email'],
            'name': profile.get('name'),
            'subscription_status': profile.get('subscription_status', 'free'),
            'created_at': profile.get('created_at'),
            'updated_at': profile.get('updated_at')
        }
        
        return success_response(clean_profile)
    
    except Exception as e:
        # Log error for CloudWatch debugging
        print(f"Error in get_me handler: {str(e)}")
        
        # Return generic error to user (don't expose internal details)
        return error_response(
            "Internal server error",
            status_code=500,
            error_code="INTERNAL_ERROR"
        )
