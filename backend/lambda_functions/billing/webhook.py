"""
POST /billing/webhook Lambda Handler
"""

import json
import os
import boto3
from typing import Dict, Any

import stripe

from shared.dynamodb import table
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
            'price_id': secret.get('price_id', ''),
            'webhook_secret': secret.get('webhook_secret', '')
        }
    
    except Exception as e:
        print(f"Error fetching Stripe config: {str(e)}")
        raise


def update_user_subscription(user_id: str, subscription_data: Dict[str, Any]) -> None:
    """Update user's subscription status in DynamoDB."""
    try:
        update_expr_parts = []
        expr_attr_names = {}
        expr_attr_values = {}
        
        for key, value in subscription_data.items():
            update_expr_parts.append(f"#{key} = :{key}")
            expr_attr_names[f"#{key}"] = key
            expr_attr_values[f":{key}"] = value
        
        update_expression = "SET " + ", ".join(update_expr_parts)
        
        table.update_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': 'PROFILE'
            },
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values
        )
        
        print(f"Updated user {user_id} subscription: {subscription_data}")
    
    except Exception as e:
        print(f"Error updating user subscription: {str(e)}")
        raise


def handle_checkout_completed(session: Dict[str, Any]) -> None:
    """Handle successful checkout."""
    print(f"Processing checkout.session.completed for session {session['id']}")
    
    user_id = session.get('metadata', {}).get('user_id')
    
    if not user_id:
        print("ERROR: No user_id in session metadata")
        return
    
    customer_id = session.get('customer')
    subscription_id = session.get('subscription')
    
    update_user_subscription(user_id, {
        'subscription_status': 'premium',
        'stripe_customer_id': customer_id,
        'stripe_subscription_id': subscription_id
    })
    
    print(f"✅ User {user_id} upgraded to premium")


def handle_subscription_deleted(subscription: Dict[str, Any]) -> None:
    """Handle subscription cancellation."""
    print(f"Processing customer.subscription.deleted for subscription {subscription['id']}")
    
    user_id = subscription.get('metadata', {}).get('user_id')
    
    if not user_id:
        customer_id = subscription.get('customer')
        print(f"No user_id in metadata, searching by customer_id: {customer_id}")
        print("ERROR: Cannot find user_id for subscription cancellation")
        return
    
    update_user_subscription(user_id, {
        'subscription_status': 'free'
    })
    
    print(f"✅ User {user_id} downgraded to free")


def handler(event, context):
    """Lambda handler for POST /billing/webhook"""
    print(f"Received webhook event")
    
    try:
        config = get_stripe_config()
        stripe.api_key = config['secret_key']
        webhook_secret = config['webhook_secret']
        
        payload = event.get('body', '')
        sig_header = event.get('headers', {}).get('Stripe-Signature', '')
        
        if not sig_header:
            print("ERROR: Missing Stripe-Signature header")
            return error_response(
                "Missing signature",
                status_code=400,
                error_code="MISSING_SIGNATURE",
                event=event
            )
        
        try:
            stripe_event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                webhook_secret
            )
        except ValueError as e:
            print(f"Invalid payload: {str(e)}")
            return error_response(
                "Invalid payload",
                status_code=400,
                error_code="INVALID_PAYLOAD",
                event=event
            )
        except stripe.error.SignatureVerificationError as e:
            print(f"Invalid signature: {str(e)}")
            return error_response(
                "Invalid signature",
                status_code=400,
                error_code="INVALID_SIGNATURE",
                event=event
            )
        
        event_type = stripe_event['type']
        print(f"Processing event type: {event_type}")
        
        if event_type == 'checkout.session.completed':
            session = stripe_event['data']['object']
            handle_checkout_completed(session)
        
        elif event_type == 'customer.subscription.deleted':
            subscription = stripe_event['data']['object']
            handle_subscription_deleted(subscription)
        
        else:
            print(f"Unhandled event type: {event_type}")
        
        return success_response({'received': True}, event=event)
    
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return success_response({'received': True, 'error': str(e)}, event=event)