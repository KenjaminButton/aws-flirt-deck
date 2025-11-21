"""
Shared response utilities for Lambda functions
"""

import json
from typing import Any, Dict, Optional


def get_cors_origin(event: Dict) -> str:
    """
    Get appropriate CORS origin based on request origin.
    Returns the request origin if it's in the allowed list, otherwise defaults to production.
    """
    origin = event.get('headers', {}).get('origin', '') or event.get('headers', {}).get('Origin', '')
    
    allowed_origins = [
        'http://localhost:3000',
        'http://localhost:5173',
        'https://flirtdecks.com',
        'https://www.flirtdecks.com'
    ]
    
    return origin if origin in allowed_origins else 'https://flirtdecks.com'


def success_response(
    data: Any,
    status_code: int = 200,
    event: Optional[Dict] = None
) -> Dict[str, Any]:
    # Get dynamic CORS origin if event provided, otherwise use production
    cors_origin = get_cors_origin(event) if event else "https://flirtdecks.com"
    
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": cors_origin,
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
            "Access-Control-Allow-Credentials": "true"
        },
        "body": json.dumps(data)
    }


def error_response(
    message: str,
    status_code: int = 400,
    error_code: Optional[str] = None,
    event: Optional[Dict] = None
) -> Dict[str, Any]:
    error_body = {
        "error": message
    }
    
    if error_code:
        error_body["code"] = error_code
    
    # Get dynamic CORS origin if event provided, otherwise use production
    cors_origin = get_cors_origin(event) if event else "https://flirtdecks.com"
    
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": cors_origin,
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
            "Access-Control-Allow-Credentials": "true"
        },
        "body": json.dumps(error_body)
    }