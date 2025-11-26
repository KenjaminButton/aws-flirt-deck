"""
CI/CD Stack: CodePipeline + CodeBuild for automated deployments

This stack creates the continuous integration/continuous deployment pipeline
for FlirtDeck. It automates the process of deploying infrastructure changes
whenever code is pushed to the main branch.

Problem solved: Manual deployments are error-prone and time-consuming.
This stack enables push-to-deploy automation via GitHub webhooks.
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
    
    Architecture:
    GitHub Push → CodePipeline (Source) → CodeBuild (Deploy) → AWS Resources
    """
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # =================================================================
        # IAM ROLE FOR CODEBUILD
        # =================================================================
        # CodeBuild needs permissions to deploy CDK stacks, access secrets,
        # and interact with various AWS services during deployment.
        # Using AdministratorAccess for simplicity - in production, you'd
        # want more restrictive permissions.
        
        build_role = iam.Role(
            self,
            "FlirtDeckBuildRole",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            description="Execution role for FlirtDeck CodeBuild project",
            managed_policies=[
                # Note: AdministratorAccess is broad - consider narrowing for production
                iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
            ]
        )
        
        # SSM permissions for CDK bootstrap version check
        # CDK stores bootstrap info in SSM Parameter Store
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

        # Secrets Manager permissions for Google OAuth credentials
        # These secrets are retrieved during CognitoStack deployment
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
        
        # =================================================================
        # CODEBUILD PROJECT
        # =================================================================
        # This is the "worker" that actually runs the build/deploy commands.
        # It reads buildspec.yml from the repo root for instructions.
        #
        # IMPORTANT: The logical ID "FlirtDeckBuildProject" must match what's
        # already deployed in CloudFormation. Changing this ID (e.g., to V2, V3)
        # causes CloudFormation to try creating a NEW resource with the same
        # physical name, resulting in conflicts.
        
        build_project = codebuild.PipelineProject(
            self,
            "FlirtDeckBuildProject",  # ← FIXED: Removed "V3" to match existing resource
            project_name="flirtdeck-backend-build",
            role=build_role,
            environment=codebuild.BuildEnvironment(
                # Standard 7.0 includes Node.js 18, Python 3.11, and other modern tools
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                compute_type=codebuild.ComputeType.SMALL,  # 3 GB memory, 2 vCPUs
                privileged=False  # Don't need Docker-in-Docker
            ),
            # BuildSpec file location - contains the actual build commands
            build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml"),
            
            # Environment variables injected from Secrets Manager
            # These become available as $GOOGLE_CLIENT_ID and $GOOGLE_CLIENT_SECRET
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
        
        # =================================================================
        # PIPELINE ARTIFACTS
        # =================================================================
        # Artifacts are the "packages" passed between pipeline stages.
        # Think of them like boxes on a conveyor belt in a factory.
        
        # Source code from GitHub
        source_output = codepipeline.Artifact("SourceOutput")
        
        # Build output (could contain compiled assets, not used much for CDK)
        build_output = codepipeline.Artifact("BuildOutput")
        
        # =================================================================
        # CODEPIPELINE
        # =================================================================
        # The pipeline orchestrates the entire deployment workflow.
        # It's like an assembly line manager coordinating different stations.
        
        pipeline = codepipeline.Pipeline(
            self,
            "FlirtDeckPipeline",
            pipeline_name="flirtdeck-backend-pipeline",
            stages=[
                # ---------------------------------------------------------
                # Stage 1: SOURCE - Pull code from GitHub
                # ---------------------------------------------------------
                # Watches the main branch and triggers on push
                codepipeline.StageProps(
                    stage_name="Source",
                    actions=[
                        codepipeline_actions.GitHubSourceAction(
                            action_name="GitHub_Source",
                            owner="KenjaminButton",
                            repo="aws-flirt-deck",
                            branch="main",
                            # GitHub personal access token stored in Secrets Manager
                            oauth_token=SecretValue.secrets_manager("github-token"),
                            output=source_output,
                            # NONE = manual trigger only (for now)
                            # Change to WEBHOOK for auto-deploy on push
                            trigger=codepipeline_actions.GitHubTrigger.NONE
                        )
                    ]
                ),
                
                # ---------------------------------------------------------
                # Stage 2: BUILD - Run CDK deploy
                # ---------------------------------------------------------
                # Executes buildspec.yml which installs dependencies and
                # runs 'cdk deploy --all'
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