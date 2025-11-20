"""
CI/CD Stack: CodePipeline + CodeBuild for automated deployments
"""

from aws_cdk import (
    Stack,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild as codebuild,
    aws_iam as iam,
    SecretValue,
)
from constructs import Construct


class CicdStack(Stack):
    """
    CI/CD Pipeline Stack
    
    Creates:
    - CodePipeline that watches GitHub repo
    - CodeBuild project that runs CDK deploy
    - IAM roles with necessary permissions
    """
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create IAM role for CodeBuild FIRST
        build_role = iam.Role(
            self,
            "FlirtDeckBuildRole",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
            ]
        )
        
        # Add SSM permissions for CDK bootstrap
        build_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ssm:GetParameter",
                    "ssm:GetParameters"
                ],
                resources=[
                    f"arn:aws:ssm:{self.region}:{self.account}:parameter/cdk-bootstrap/*",
                    f"arn:aws:ssm:{self.region}:{self.account}:parameter/cdk-bootstrap/hnb659fds/version"
                ]
            )
        )


        # Add Secrets Manager permissions for Google OAuth
        build_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "secretsmanager:GetSecretValue"
                ],
                resources=[
                    f"arn:aws:secretsmanager:{self.region}:{self.account}:secret:google-oauth-*"
                ]
            )
        )
        
        # Create CodeBuild project with the role
        build_project = codebuild.PipelineProject(
            self,
            "FlirtDeckBuildProjectV3",
            project_name="flirtdeck-backend-build",
            role=build_role,  # Use our custom role
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                compute_type=codebuild.ComputeType.SMALL,
                privileged=False
            ),
            build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml"),
            
            # Environment variables for Google OAuth
            environment_variables={
                "GOOGLE_CLIENT_ID": codebuild.BuildEnvironmentVariable(
                    value="google-oauth-client-id",
                    type=codebuild.BuildEnvironmentVariableType.SECRETS_MANAGER
                ),
                "GOOGLE_CLIENT_SECRET": codebuild.BuildEnvironmentVariable(
                    value="google-oauth-client-secret",
                    type=codebuild.BuildEnvironmentVariableType.SECRETS_MANAGER
                )
            }
        )
        
        # Create source artifact (code from GitHub)
        source_output = codepipeline.Artifact("SourceOutput")
        
        # Create build artifact (built application)
        build_output = codepipeline.Artifact("BuildOutput")
        
        # Create the pipeline
        pipeline = codepipeline.Pipeline(
            self,
            "FlirtDeckPipeline",
            pipeline_name="flirtdeck-backend-pipeline",
            stages=[
                # Stage 1: Pull code from GitHub
                codepipeline.StageProps(
                    stage_name="Source",
                    actions=[
                        codepipeline_actions.GitHubSourceAction(
                            action_name="GitHub_Source",
                            owner="KenjaminButton",
                            repo="aws-flirt-deck",
                            branch="main",
                            oauth_token=SecretValue.secrets_manager("github-token"),
                            output=source_output,
                            trigger=codepipeline_actions.GitHubTrigger.NONE
                        )
                    ]
                ),
                
                # Stage 2: Build and deploy with CDK
                codepipeline.StageProps(
                    stage_name="Build",
                    actions=[
                        codepipeline_actions.CodeBuildAction(
                            action_name="CDK_Deploy",
                            project=build_project,
                            input=source_output,
                            outputs=[build_output]
                        )
                    ]
                )
            ]
        )