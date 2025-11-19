"""
Shared response utilities for Lambda functions
"""

import json
from typing import Any, Dict, Optional


def success_response(
    data: Any,
    status_code: int = 200
) -> Dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "https://d2lobh4zu3vjy5.cloudfront.net",
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
    error_body = {
        "error": message
    }
    
    if error_code:
        error_body["code"] = error_code
    
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "https://d2lobh4zu3vjy5.cloudfront.net",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
            "Access-Control-Allow-Credentials": "true"
        },
        "body": json.dumps(error_body)
    }