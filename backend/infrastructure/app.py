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

# Create the CDK app instance
# This is the root construct that contains all our stacks
app = cdk.App()

# Deploy DatabaseStack to us-west-2
# We explicitly set the region to ensure consistency across deployments
# Environment is set using account/region from AWS CLI configuration
DatabaseStack(
    app, 
    "DatabaseStack",
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),  # Gets account from 'aws configure'
        region='us-west-2'  # Hardcoded to us-west-2 per project requirements
    ),
    description="DynamoDB table for FlirtDeck multi-tenant data storage"
)

# Synthesize all stacks into CloudFormation templates
# This generates the JSON templates that AWS will use to create resources
app.synth()