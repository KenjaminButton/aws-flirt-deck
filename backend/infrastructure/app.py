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

# Synthesize all stacks into CloudFormation templates
# This generates the JSON templates that AWS will use to create resources
app.synth()
