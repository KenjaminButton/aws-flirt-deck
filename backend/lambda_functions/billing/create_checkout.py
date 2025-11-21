"""
POST /billing/create-checkout Lambda Handler
"""

import json
import os
import boto3
from typing import Dict, Any

import stripe

from shared.responses import success_response, error_response


secretsmanager = boto3.client('secretsmanager', region_name='us-west-2')


def get_stripe_config() -> Dict[str, str]:
    """Fetch Stripe configuration from AWS Secrets Manager."""
    try:
        response = secretsmanager.get_secret_value(
            SecretId='flirtdeck/stripe'
        )
        
        secret = json.loads(response['SecretString'])
        
        return {
            'secret_key': secret['secret_key'],
            'price_id': secret['price_id']
        }
    
    except Exception as e:
        print(f"Error fetching Stripe config from Secrets Manager: {str(e)}")
        raise


def handler(event, context):
    """Lambda handler for POST /billing/create-checkout"""
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract user info from JWT
        authorizer = event.get('requestContext', {}).get('authorizer', {})
        claims = authorizer.get('claims', {})
        
        user_id = claims.get('sub')
        email = claims.get('email')
        
        if not user_id or not email:
            return error_response(
                "Missing user information",
                status_code=401,
                error_code="UNAUTHORIZED",
                event=event
            )
        
        # Get Stripe configuration
        print("Fetching Stripe config from Secrets Manager...")
        config = get_stripe_config()
        
        stripe.api_key = config['secret_key']
        
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
        
        # Create or retrieve Stripe Customer
        print(f"Creating/retrieving Stripe customer for user {user_id}")
        
        customers = stripe.Customer.list(email=email, limit=1)
        
        if customers.data:
            customer = customers.data[0]
            print(f"Found existing customer: {customer.id}")
        else:
            customer = stripe.Customer.create(
                email=email,
                metadata={
                    'user_id': user_id
                }
            )
            print(f"Created new customer: {customer.id}")
        
        # Create Checkout Session
        print("Creating Checkout Session...")
        
        checkout_session = stripe.checkout.Session.create(
            customer=customer.id,
            mode='subscription',
            line_items=[{
                'price': config['price_id'],
                'quantity': 1
            }],
            success_url=f"{frontend_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{frontend_url}/billing/cancel",
            metadata={
                'user_id': user_id
            },
            customer_email=email if not customers.data else None,
            subscription_data={
                'metadata': {
                    'user_id': user_id
                }
            }
        )
        
        print(f"Checkout session created: {checkout_session.id}")
        
        return success_response({
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        }, event=event)
    
    except stripe.error.StripeError as e:
        print(f"Stripe error: {str(e)}")
        return error_response(
            "Payment processing error. Please try again.",
            status_code=500,
            error_code="STRIPE_ERROR",
            event=event
        )
    
    except Exception as e:
        print(f"Error creating checkout session: {str(e)}")
        return error_response(
            "Failed to create checkout session",
            status_code=500,
            error_code="INTERNAL_ERROR",
            event=event
        )