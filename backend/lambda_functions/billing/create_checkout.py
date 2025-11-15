"""
POST /billing/create-checkout Lambda Handler

Creates a Stripe Checkout Session for upgrading to Premium.

Flow:
1. Get user info from JWT token
2. Fetch Stripe keys from AWS Secrets Manager
3. Create/retrieve Stripe Customer
4. Create Checkout Session
5. Return checkout URL to frontend

The user will be redirected to Stripe's hosted checkout page.
"""

import json
import os
import boto3
from typing import Dict, Any

# Import Stripe SDK
# We'll install this via Lambda Layer or package it with the function
import stripe

from shared.responses import success_response, error_response


# Initialize AWS clients
secretsmanager = boto3.client('secretsmanager', region_name='us-west-2')


def get_stripe_config() -> Dict[str, str]:
    """
    Fetch Stripe configuration from AWS Secrets Manager.
    
    Returns:
        Dict with 'secret_key' and 'price_id'
    
    Raises:
        Exception if secret cannot be retrieved
    """
    try:
        response = secretsmanager.get_secret_value(
            SecretId='flirtdeck/stripe'
        )
        
        # Parse the JSON string
        secret = json.loads(response['SecretString'])
        
        return {
            'secret_key': secret['secret_key'],
            'price_id': secret['price_id']
        }
    
    except Exception as e:
        print(f"Error fetching Stripe config from Secrets Manager: {str(e)}")
        raise


def handler(event, context):
    """
    Lambda handler for POST /billing/create-checkout
    
    Creates a Stripe Checkout Session and returns the URL.
    """
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
                error_code="UNAUTHORIZED"
            )
        
        # Get Stripe configuration
        print("Fetching Stripe config from Secrets Manager...")
        config = get_stripe_config()
        
        # Initialize Stripe with secret key
        stripe.api_key = config['secret_key']
        
        # Get frontend URL from environment variable
        # We'll set this in CDK
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
        
        # Create or retrieve Stripe Customer
        print(f"Creating/retrieving Stripe customer for user {user_id}")
        
        # Search for existing customer by email
        customers = stripe.Customer.list(email=email, limit=1)
        
        if customers.data:
            # Customer exists
            customer = customers.data[0]
            print(f"Found existing customer: {customer.id}")
        else:
            # Create new customer
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
            
            # Payment settings
            mode='subscription',
            line_items=[{
                'price': config['price_id'],
                'quantity': 1
            }],
            
            # Redirect URLs
            success_url=f"{frontend_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{frontend_url}/billing/cancel",
            
            # Metadata to track which user this belongs to
            metadata={
                'user_id': user_id
            },
            
            # Pre-fill customer email
            customer_email=email if not customers.data else None,
            
            # Subscription settings
            subscription_data={
                'metadata': {
                    'user_id': user_id
                }
            }
        )
        
        print(f"Checkout session created: {checkout_session.id}")
        
        # Return the checkout URL to frontend
        return success_response({
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        })
    
    except stripe.error.StripeError as e:
        # Stripe-specific errors
        print(f"Stripe error: {str(e)}")
        return error_response(
            "Payment processing error. Please try again.",
            status_code=500,
            error_code="STRIPE_ERROR"
        )
    
    except Exception as e:
        # General errors
        print(f"Error creating checkout session: {str(e)}")
        return error_response(
            "Failed to create checkout session",
            status_code=500,
            error_code="INTERNAL_ERROR"
        )
