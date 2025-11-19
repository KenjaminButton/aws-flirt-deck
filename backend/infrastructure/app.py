#!/usr/bin/env python3
"""
FlirtDeck CDK App - Main Entry Point

This file is the entry point for the CDK application.
It instantiates all infrastructure stacks and synthesizes them into CloudFormation.
"""

import os
import aws_cdk as cdk

# Import our custom stacks
from infrastructure.database_stack import DatabaseStack
from infrastructure.cognito_stack import CognitoStack
from infrastructure.api_stack import ApiStack
from infrastructure.frontend_stack import FrontendStack

# Create the CDK app instance
# This is the root construct that contains all our stacks
app = cdk.App()

# Define the environment (account + region) for all stacks
# This ensures consistency across deployments
env = cdk.Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),  # Gets account from 'aws configure'
    region='us-west-2'  # Hardcoded to us-west-2 per project requirements
)

# Deploy DatabaseStack to us-west-2
# Creates DynamoDB table for multi-tenant data storage
database_stack = DatabaseStack(
    app, 
    "DatabaseStack",
    env=env,
    description="DynamoDB table for FlirtDeck multi-tenant data storage"
)

# Deploy CognitoStack to us-west-2
# Creates User Pool with Google OAuth integration
# Requires GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables
cognito_stack = CognitoStack(
    app,
    "CognitoStack",
    env=env,
    description="Cognito User Pool with Google OAuth for user authentication"
)

# Deploy ApiStack to us-west-2
# Creates API Gateway with Lambda functions
# Depends on both DatabaseStack and CognitoStack
api_stack = ApiStack(
    app,
    "ApiStack",
    user_pool=cognito_stack.user_pool,  # Pass User Pool for authorization
    user_pool_client=cognito_stack.user_pool_client,  
    table_name=database_stack.table.table_name,  # Pass table name for Lambda env vars
    env=env,
    description="API Gateway with Lambda functions for backend endpoints"
)

# Set stack dependencies
# Ensures stacks are deployed in the correct order
api_stack.add_dependency(database_stack)
api_stack.add_dependency(cognito_stack)

# Deploy FrontendStack to us-west-2
# Creates S3 bucket and CloudFront distribution for React app
frontend_stack = FrontendStack(
    app,
    "FrontendStack",
    env=env,
    description="S3 + CloudFront hosting for React frontend"
)

# Synthesize all stacks into CloudFormation templates
# This generates the JSON templates that AWS will use to create resources
app.synth()
