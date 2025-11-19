"""
CI/CD Stack: Automated deployment pipeline for FlirtDeck backend

This stack creates a CodePipeline that automatically deploys backend changes
whenever code is pushed to the main branch on GitHub.

Think of it like a robot that watches your GitHub repo and automatically
runs 'cdk deploy' whenever you push new code.
"""

from aws_cdk import (
    Stack,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_iam as iam,
    Tags,
    SecretValue
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
        
        # Step 1: Create the CodeBuild project
        # This is like hiring a construction worker that knows how to build your app
        build_project = codebuild.PipelineProject(
            self,
            "FlirtDeckBuildProject",
            project_name="flirtdeck-backend-build",
            description="Builds and deploys FlirtDeck backend infrastructure",
            
            # Build environment: Ubuntu with Python runtime
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,  # Ubuntu with Node 18, Python 3.11
                compute_type=codebuild.ComputeType.SMALL,  # 3 GB RAM, 2 vCPUs (cheapest option)
                privileged=False  # Don't need Docker
            ),
            
            # Build commands are defined in buildspec.yml (we'll create this next)
            build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml")
        )
        
        # Grant CodeBuild permission to deploy CDK stacks
        # This allows the build to create/update AWS resources
        build_project.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "cloudformation:*",
                    "s3:*",
                    "lambda:*",
                    "apigateway:*",
                    "cognito-idp:*",
                    "dynamodb:*",
                    "iam:*",
                    "cloudfront:*"
                ],
                resources=["*"]
            )
        )
        
        # Step 2: Create the CodePipeline
        # This is the overall workflow manager
        pipeline = codepipeline.Pipeline(
            self,
            "FlirtDeckPipeline",
            pipeline_name="flirtdeck-backend-pipeline",
            restart_execution_on_update=True  # Automatically re-run pipeline after updates
        )
        
        # Stage 1: Source - Connect to GitHub
        # This stage watches your GitHub repo for changes
        source_output = codepipeline.Artifact("SourceOutput")
        
        source_action = codepipeline_actions.GitHubSourceAction(
            action_name="GitHub_Source",
            owner="KenjaminButton",  # Your GitHub username
            repo="aws-flirt-deck",   # Your repo name
            branch="main",           # Branch to monitor
            oauth_token=SecretValue.secrets_manager("github-token"),  # We'll create this secret next
            output=source_output,
            trigger=codepipeline_actions.GitHubTrigger.WEBHOOK  # Trigger on every push
        )
        
        pipeline.add_stage(
            stage_name="Source",
            actions=[source_action]
        )
        
        # Stage 2: Build - Run CDK deploy
        # This stage builds and deploys your infrastructure
        build_output = codepipeline.Artifact("BuildOutput")
        
        build_action = codepipeline_actions.CodeBuildAction(
            action_name="CDK_Deploy",
            project=build_project,
            input=source_output,
            outputs=[build_output]
        )
        
        pipeline.add_stage(
            stage_name="Deploy",
            actions=[build_action]
        )
        
        # Add resource tags
        Tags.of(self).add("Project", "FlirtDeck")
        Tags.of(self).add("Environment", "Production")
        Tags.of(self).add("ManagedBy", "CDK")