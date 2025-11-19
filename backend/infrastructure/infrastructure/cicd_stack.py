"""
CI/CD Stack: Automated deployment pipeline for FlirtDeck backend

This stack creates a CodePipeline that automatically deploys backend changes
whenever code is pushed to the main branch on GitHub.

Think of it like a robot that watches your GitHub repo and automatically
runs 'cdk deploy' whenever you push new code.
"""

from aws_cdk import (
    Stack,
    Tags
)
from constructs import Construct


class CicdStack(Stack):
    """
    CicdStack: Creates CI/CD pipeline for automated deployments
    
    Components:
    - CodePipeline: Orchestrates the deployment workflow
    - CodeBuild: Runs tests and deploys infrastructure
    - GitHub connection: Monitors repo for changes
    """
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # TODO: We'll add the pipeline resources here next
        
        # Add resource tags
        Tags.of(self).add("Project", "FlirtDeck")
        Tags.of(self).add("Environment", "Production")
        Tags.of(self).add("ManagedBy", "CDK")