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

        # Create Stripe Lambda Layer
        # This layer contains the Stripe Python library
        self.stripe_layer = lambda_.LayerVersion(
            self,
            "StripeLayer",
            code=lambda_.Code.from_asset(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "..",
                    "layers",
                    "stripe",
                    "stripe-layer.zip"
                )
            ),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
            description="Stripe Python SDK for billing functions"
        )

        # Create IAM role for Lambda execution
        self.lambda_role = iam.Role(
            self,
            "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Execution role for FlirtDeck Lambda functions",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )

        # Grant DynamoDB permissions to Lambda role
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

        # Grant Secrets Manager permissions to Lambda role
        # Allows Lambda to read Stripe keys from AWS Secrets Manager
        self.lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "secretsmanager:GetSecretValue"
                ],
                resources=[
                    f"arn:aws:secretsmanager:{self.region}:{self.account}:secret:flirtdeck/stripe-*"
                ]
            )
        )

        # Create REST API Gateway
        self.api = apigw.RestApi(
            self,
            "FlirtDeckApi",
            rest_api_name="flirtdeck-api",
            description="FlirtDeck Backend API",
            deploy_options=apigw.StageOptions(
                stage_name="prod",
                throttling_rate_limit=100,
                throttling_burst_limit=200,
            ),
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=["http://localhost:5173"],
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

        # Create Cognito authorizer
        self.authorizer = apigw.CognitoUserPoolsAuthorizer(
            self,
            "CognitoAuthorizer",
            cognito_user_pools=[user_pool],
            authorizer_name="cognito-authorizer",
            identity_source="method.request.header.Authorization",
        )

        # ==================== /auth ENDPOINTS ====================
        auth_resource = self.api.root.add_resource("auth")

        get_me_lambda = self.create_lambda_function(
            function_id="GetMeFunction",
            handler_path="auth",
            handler_file="get_me",
            description="Get current user profile",
        )

        auth_resource.add_resource("me").add_method(
            "GET",
            apigw.LambdaIntegration(get_me_lambda),
            authorizer=self.authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )

        # ==================== /questions ENDPOINTS ====================
        questions_resource = self.api.root.add_resource("questions")

        get_random_lambda = self.create_lambda_function(
            function_id="GetRandomQuestionFunction",
            handler_path="questions",
            handler_file="get_random",
            description="Get random question by category",
        )

        questions_resource.add_resource("random").add_method(
            "GET",
            apigw.LambdaIntegration(get_random_lambda),
            authorizer=self.authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )

        # ==================== /connections ENDPOINTS ====================
        connections_resource = self.api.root.add_resource("connections")

        # GET /connections - List all connections
        list_connections_lambda = self.create_lambda_function(
            function_id="ListConnectionsFunction",
            handler_path="connections",
            handler_file="list",
            description="List all connections for user",
        )

        connections_resource.add_method(
            "GET",
            apigw.LambdaIntegration(list_connections_lambda),
            authorizer=self.authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )

        # POST /connections - Create new connection
        create_connection_lambda = self.create_lambda_function(
            function_id="CreateConnectionFunction",
            handler_path="connections",
            handler_file="create",
            description="Create a new connection",
        )

        connections_resource.add_method(
            "POST",
            apigw.LambdaIntegration(create_connection_lambda),
            authorizer=self.authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )

        # DELETE /connections/{connection_id} - Delete a connection
        connection_id_resource = connections_resource.add_resource(
            "{connection_id}",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=["http://localhost:5173"],
                allow_methods=["DELETE", "OPTIONS"],
                allow_headers=[
                    "Content-Type",
                    "Authorization",
                    "X-Amz-Date",
                    "X-Api-Key",
                    "X-Amz-Security-Token",
                ],
                allow_credentials=True,
            )
        )
        
        delete_connection_lambda = self.create_lambda_function(
            function_id="DeleteConnectionFunction",
            handler_path="connections",
            handler_file="delete",
            description="Delete a connection",
        )

        connection_id_resource.add_method(
            "DELETE",
            apigw.LambdaIntegration(delete_connection_lambda),
            authorizer=self.authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )

        # POST /connections/{connection_id}/usage
        usage_resource = connection_id_resource.add_resource("usage")
        
        create_usage_lambda = self.create_lambda_function(
            function_id="CreateUsageFunction",
            handler_path="usage",
            handler_file="create",
            description="Record question usage with connection",
        )

        usage_resource.add_method(
            "POST",
            apigw.LambdaIntegration(create_usage_lambda),
            authorizer=self.authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )

        # GET /connections/{connection_id}/usage - List usage records
        list_usage_lambda = self.create_lambda_function(
            function_id="ListUsageFunction",
            handler_path="usage",
            handler_file="list",
            description="List all usage records for connection",
        )

        usage_resource.add_method(
            "GET",
            apigw.LambdaIntegration(list_usage_lambda),
            authorizer=self.authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )

        # /connections/{connection_id}/usage/{usage_id} resource
        # Add explicit CORS for PUT and DELETE on usage records
        usage_id_resource = usage_resource.add_resource(
            "{usage_id}",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=["http://localhost:5173"],
                allow_methods=["GET", "PUT", "DELETE", "OPTIONS"],
                allow_headers=[
                    "Content-Type",
                    "Authorization",
                    "X-Amz-Date",
                    "X-Api-Key",
                    "X-Amz-Security-Token",
                ],
                allow_credentials=True,
            )
        )
        
        # PUT /connections/{connection_id}/usage/{usage_id} - Update usage
        update_usage_lambda = self.create_lambda_function(
            function_id="UpdateUsageFunction",
            handler_path="usage",
            handler_file="update",
            description="Update usage record answers",
        )

        usage_id_resource.add_method(
            "PUT",
            apigw.LambdaIntegration(update_usage_lambda),
            authorizer=self.authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )
        
        # DELETE /connections/{connection_id}/usage/{usage_id} - Delete usage
        delete_usage_lambda = self.create_lambda_function(
            function_id="DeleteUsageFunction",
            handler_path="usage",
            handler_file="delete",
            description="Delete usage record",
        )

        usage_id_resource.add_method(
            "DELETE",
            apigw.LambdaIntegration(delete_usage_lambda),
            authorizer=self.authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )

        # ==================== /billing ENDPOINTS ====================
        billing_resource = self.api.root.add_resource("billing")

        # POST /billing/create-checkout - Create Stripe checkout session
        create_checkout_lambda = self.create_lambda_function(
            function_id="CreateCheckoutFunction",
            handler_path="billing",
            handler_file="create_checkout",
            description="Create Stripe checkout session for premium upgrade",
            layers=[self.stripe_layer],
        )

        billing_resource.add_resource("create-checkout").add_method(
            "POST",
            apigw.LambdaIntegration(create_checkout_lambda),
            authorizer=self.authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )


        # Add resource tags
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
        layers: list = None,
    ) -> lambda_.Function:
        """Create Lambda function with consistent configuration"""

        code_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "lambda_functions"
        )

        return lambda_.Function(
            self,
            function_id,
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler=f"{handler_path}.{handler_file}.handler",
            code=lambda_.Code.from_asset(
                code_path,
                exclude=[
                    "**/__pycache__",
                    "**/*.pyc",
                    "**/seed_data.py",
                    "**/.gitkeep",
                ]
            ),
            role=self.lambda_role,
            timeout=Duration.seconds(timeout),
            description=description,
            layers=layers or [],
            environment={
                "TABLE_NAME": self.table_name,
                "USER_POOL_ID": self.user_pool.user_pool_id,
            },
        )