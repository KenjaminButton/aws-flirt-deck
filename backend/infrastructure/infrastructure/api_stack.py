"""
API Stack: Creates API Gateway, Lambda functions, and integrations

This stack is the backend API layer for FlirtDeck.
It creates:
- REST API Gateway with Cognito authorization
- Lambda functions for API endpoints
- IAM roles and permissions
- CORS configuration
"""

from aws_cdk import (
    Stack,
    aws_apigateway as apigw,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_cognito as cognito,
    Duration,
    Tags,
)
from constructs import Construct
import os


class ApiStack(Stack):
    """
    ApiStack: Creates the API Gateway and Lambda functions

    This stack depends on:
    - DatabaseStack (needs DynamoDB table)
    - CognitoStack (needs User Pool for authorization)
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        user_pool: cognito.IUserPool,
        table_name: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Store references for use in Lambda functions
        self.user_pool = user_pool
        self.table_name = table_name

        # Create IAM role for Lambda execution
        # This role gives Lambda permission to:
        # - Write logs to CloudWatch
        # - Read/write to DynamoDB
        self.lambda_role = iam.Role(
            self,
            "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Execution role for FlirtDeck Lambda functions",
            managed_policies=[
                # Allows Lambda to write logs to CloudWatch
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )

        # Grant DynamoDB permissions to Lambda role
        # Allows read and write access to the flirtdeck-table
        self.lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                ],
                resources=[
                    f"arn:aws:dynamodb:{self.region}:{self.account}:table/{table_name}",
                    f"arn:aws:dynamodb:{self.region}:{self.account}:table/{table_name}/index/*",
                ],
            )
        )

        # Create REST API Gateway
        # This is the main entry point for all API requests
        self.api = apigw.RestApi(
            self,
            "FlirtDeckApi",
            rest_api_name="flirtdeck-api",
            description="FlirtDeck Backend API",
            # Deploy to 'prod' stage automatically
            deploy_options=apigw.StageOptions(
                stage_name="prod",
                throttling_rate_limit=100,  # Max requests per second
                throttling_burst_limit=200,  # Max concurrent requests
            ),
            # Enable CORS for frontend requests
            # Allows localhost and CloudFront to call this API
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=["http://localhost:5173"],  # Add CloudFront later
                allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                allow_headers=[
                    "Content-Type",
                    "Authorization",
                    "X-Amz-Date",
                    "X-Api-Key",
                    "X-Amz-Security-Token",
                ],
                allow_credentials=True,
            ),
        )

        # Create Cognito authorizer for API Gateway
        # This validates JWT tokens from Cognito on every request
        self.authorizer = apigw.CognitoUserPoolsAuthorizer(
            self,
            "CognitoAuthorizer",
            cognito_user_pools=[user_pool],
            authorizer_name="cognito-authorizer",
            identity_source="method.request.header.Authorization",
        )

        # Create /auth resource and /auth/me endpoint
        auth_resource = self.api.root.add_resource("auth")

        # Create GET /auth/me Lambda function
        get_me_lambda = self.create_lambda_function(
            function_id="GetMeFunction",
            handler_path="lambda_functions/auth",
            handler_file="get_me",
            description="Get current user profile",
        )

        # Add GET /auth/me endpoint to API Gateway
        # Requires Cognito authorization
        auth_resource.add_resource("me").add_method(
            "GET",
            apigw.LambdaIntegration(get_me_lambda),
            authorizer=self.authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )

        # Add resource tags for cost tracking
        Tags.of(self).add("Project", "FlirtDeck")
        Tags.of(self).add("Environment", "Production")
        Tags.of(self).add("ManagedBy", "CDK")

    def create_lambda_function(
        self,
        function_id: str,
        handler_path: str,
        handler_file: str,
        description: str,
        timeout: int = 30,
    ) -> lambda_.Function:
        """
        Helper method to create Lambda functions with consistent configuration

        Args:
            function_id: CDK construct ID for the Lambda
            handler_path: Path to Lambda code (relative to backend/)
            handler_file: Python file name (without .py)
            description: Human-readable description
            timeout: Function timeout in seconds (default: 30)

        Returns:
            Lambda Function construct
        """

        # Path to the directory containing both lambda code AND shared utilities
        # We need to go up to backend/ so Lambda can import from shared/
        code_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",  # This takes us to backend/ directory
        )

        return lambda_.Function(
            self,
            function_id,
            runtime=lambda_.Runtime.PYTHON_3_9,
            # Handler path is now relative to backend/ directory
            handler=f"{handler_path.replace('/', '.')}.{handler_file}.handler",
            code=lambda_.Code.from_asset(
                code_path,
                # Exclude unnecessary files to keep package small
                exclude=[
                    "infrastructure/*",
                    ".git/*",
                    "*.pyc",
                    "__pycache__/*",
                    ".pytest_cache/*",
                    "*.egg-info/*",
                ],
            ),
            role=self.lambda_role,
            timeout=Duration.seconds(timeout),
            description=description,
            environment={
                "TABLE_NAME": self.table_name,
                "USER_POOL_ID": self.user_pool.user_pool_id,
            },
        )
