"""
Shared DynamoDB utilities for Lambda functions

Provides helper functions to interact with the flirtdeck-table.
Uses single-table design with PK/SK pattern for multi-tenant data.
"""

import boto3
import os
from typing import Dict, Optional, Any
from datetime import datetime

# Initialize DynamoDB client
# boto3 automatically uses AWS credentials from Lambda execution environment
dynamodb = boto3.resource('dynamodb')

# Get table name from environment variable (set by CDK)
TABLE_NAME = os.environ.get('TABLE_NAME', 'flirtdeck-table')
table = dynamodb.Table(TABLE_NAME)


def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a user's profile from DynamoDB
    
    Args:
        user_id: Cognito user ID (sub from JWT token)
    
    Returns:
        User profile dict if found, None if not found
    
    Example:
        profile = get_user_profile("abc123")
        # Returns: {"user_id": "abc123", "email": "user@example.com", ...}
    """
    try:
        response = table.get_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': 'PROFILE'
            }
        )
        
        # Return the item if found, None if not
        return response.get('Item')
    
    except Exception as e:
        print(f"Error getting user profile: {str(e)}")
        return None


def create_user_profile(user_id: str, email: str, name: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new user profile in DynamoDB
    
    This is called on first Google login to create the user's record.
    
    Args:
        user_id: Cognito user ID (sub from JWT token)
        email: User's email address
        name: User's full name (optional)
    
    Returns:
        The created user profile dict
    
    Example:
        profile = create_user_profile("abc123", "user@example.com", "John Doe")
    """
    timestamp = datetime.utcnow().isoformat()
    
    # Single-table design: USER#abc123 as partition key
    profile = {
        'PK': f'USER#{user_id}',
        'SK': 'PROFILE',
        'user_id': user_id,
        'email': email,
        'name': name,
        'subscription_status': 'free',  # Default to free tier
        'created_at': timestamp,
        'updated_at': timestamp,
        
        # GSI1 for querying users by email (future feature)
        'GSI1PK': f'EMAIL#{email}',
        'GSI1SK': f'USER#{user_id}'
    }
    
    try:
        table.put_item(Item=profile)
        return profile
    
    except Exception as e:
        print(f"Error creating user profile: {str(e)}")
        raise


def update_user_profile(user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a user's profile in DynamoDB
    
    Args:
        user_id: Cognito user ID
        updates: Dictionary of fields to update
    
    Returns:
        Updated user profile dict
    
    Example:
        updated = update_user_profile("abc123", {"subscription_status": "premium"})
    """
    timestamp = datetime.utcnow().isoformat()
    updates['updated_at'] = timestamp
    
    # Build update expression dynamically
    update_expression = "SET " + ", ".join([f"#{k} = :{k}" for k in updates.keys()])
    expression_attribute_names = {f"#{k}": k for k in updates.keys()}
    expression_attribute_values = {f":{k}": v for k, v in updates.items()}
    
    try:
        response = table.update_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': 'PROFILE'
            },
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues='ALL_NEW'
        )
        
        return response.get('Attributes')
    
    except Exception as e:
        print(f"Error updating user profile: {str(e)}")
        raise