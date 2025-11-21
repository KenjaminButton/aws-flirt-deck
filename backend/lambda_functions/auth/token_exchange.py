# Force redeploy - updated CORS headers v3
"""
POST /auth/token Lambda Handler
Exchanges authorization code for tokens after OAuth redirect.
"""

import json
import os
import sys
import urllib.request
import urllib.parse

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.responses import success_response, error_response


def handler(event, context):
    
    try:
        body = json.loads(event.get('body', '{}'))
        code = body.get('code')
        
        if not code:
            return error_response("Missing authorization code", status_code=400, event=event)
                
        cognito_domain = os.environ.get('COGNITO_DOMAIN')
        client_id = os.environ.get('COGNITO_CLIENT_ID')
        redirect_uri = body.get('redirect_uri')

        token_url = f"https://{cognito_domain}/oauth2/token"
        
        data = {
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'code': code,
            'redirect_uri': redirect_uri
        }
        
        encoded_data = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(token_url, data=encoded_data, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            return success_response({
                'id_token': response_data.get('id_token'),
                'access_token': response_data.get('access_token'),
                'refresh_token': response_data.get('refresh_token')
            }, event=event)
    
    except Exception as e:
        print(f"Token exchange error: {str(e)}")
        return error_response("Token exchange failed", status_code=401, event=event)
