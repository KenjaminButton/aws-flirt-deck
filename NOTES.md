```python
"""
Shared response utilities for Lambda functions
Provides consistent JSON response formatting for API Gateway.
All Lambda functions should use these helpers to ensure uniform response structure.
"""

import json
from typing import Any, Dict, Optional


def success_response(
    data: Any,
    status_code: int = 200
) -> Dict[str, Any]:
    """
    Create a successful API response
    
    Args:
        data: The response data (will be JSON serialized)
        status_code: HTTP status code (default: 200)
    
    Returns:
        Dict formatted for API Gateway Lambda proxy integration
    
    Example:
        return success_response({"user_id": "123", "email": "user@example.com"})
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            # CORS headers for browser requests
            "Access-Control-Allow-Origin": "http://localhost:5173",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
            "Access-Control-Allow-Credentials": "true"
        },
        "body": json.dumps(data)
    }


def error_response(
    message: str,
    status_code: int = 400,
    error_code: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create an error API response
    
    Args:
        message: Human-readable error message
        status_code: HTTP status code (default: 400 Bad Request)
        error_code: Optional machine-readable error code
    
    Returns:
        Dict formatted for API Gateway Lambda proxy integration
    
    Example:
        return error_response("User not found", status_code=404, error_code="USER_NOT_FOUND")
    """
    error_body = {
        "error": message
    }
    
    # Add error code if provided
    if error_code:
        error_body["code"] = error_code
    
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            # CORS headers for browser requests
            "Access-Control-Allow-Origin": "http://localhost:5173",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
            "Access-Control-Allow-Credentials": "true"
        },
        "body": json.dumps(error_body)
    }
```