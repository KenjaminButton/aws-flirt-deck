from aws_cdk import (
    Stack,
    aws_cognito as cognito,
    CfnOutput,
    Tags
)
from constructs import Construct
import os


class CognitoStack(Stack):
    """
    CognitoStack: Creates Cognito User Pool with Google OAuth integration
    
    This stack handles user authentication for FlirtDeck:
    - User Pool for managing user accounts
    - Google as federated identity provider (OAuth 2.0)
    - OAuth flows for web application authentication
    - Email-based sign-in with password requirements
    """
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Get Google OAuth credentials from environment variables
        # These should be set before running cdk deploy
        google_client_id = os.getenv('GOOGLE_CLIENT_ID')
        google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        # Validate that credentials are provided
        if not google_client_id or not google_client_secret:
            raise ValueError(
                "GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables must be set. "
                "Export them before running cdk deploy."
            )
        
        # Create Cognito User Pool
        # This is the main user directory that stores user accounts
        self.user_pool = cognito.UserPool(
            self,
            "FlirtDeckUserPool",
            user_pool_name="flirtdeck-users",
            
            # Allow users to sign in with email address
            sign_in_aliases=cognito.SignInAliases(
                email=True,
                username=False  # Disable username sign-in, email only
            ),
            
            # Require email verification when users sign up
            # Email will be sent automatically by Cognito
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            
            # Password policy requirements
            # Enforces strong passwords for security
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_uppercase=True,
                require_lowercase=True,
                require_digits=True,
                require_symbols=False  # Optional: make it easier for users
            ),
            
            # Standard attributes that will be collected
            # Email is required for authentication
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(
                    required=True,
                    mutable=True  # Users can update their email
                )
            ),
            
            # Account recovery options
            # Users can reset password via email
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            
            # Self sign-up: allow users to create accounts without admin approval
            self_sign_up_enabled=True
        )
        
        # Add Cognito domain for hosted UI
        # This creates a URL like: flirtdeck-dev-{random}.auth.us-west-2.amazoncognito.com
        # The hosted UI provides login/signup pages automatically
        # Note: Domain must be globally unique across all AWS accounts
        user_pool_domain = self.user_pool.add_domain(
            "CognitoDomain",
            cognito_domain=cognito.CognitoDomainOptions(
                # Using your initials + timestamp to make it unique
                # Change this prefix if deployment fails due to domain conflict
                domain_prefix="flirtdeck-kb-dev"
            )
        )
        
        # Create User Pool Client (the app that uses Cognito)
        # This represents your frontend application
        self.user_pool_client = cognito.UserPoolClient(
            self,
            "FlirtDeckClient",
            user_pool=self.user_pool,
            user_pool_client_name="flirtdeck-web-client",
            
            # Generate client secret: False for public web apps (like SPAs)
            # True would be for server-side apps that can keep secrets
            generate_secret=False,
            
            supported_identity_providers=[
                cognito.UserPoolClientIdentityProvider.GOOGLE
            ],

            # OAuth 2.0 settings
            # These define how authentication flows work
            o_auth=cognito.OAuthSettings(
                # Authorization code flow: Most secure for web apps
                # Implicit flow: Simpler but less secure (included for compatibility)
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True,
                    implicit_code_grant=True
                ),
                
                # Scopes define what user data the app can access
                # openid: Required for OAuth
                # email: Access user's email address
                # profile: Access user's basic profile info
                scopes=[
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.EMAIL,
                    cognito.OAuthScope.PROFILE
                ],
                
                # Callback URLs: Where Cognito redirects after successful login
                # localhost for local development
                # Will add CloudFront URL later when we deploy frontend
                callback_urls=[
                    "http://localhost:5173",
                    "http://localhost:5173/callback",
                    "http://localhost:5173/auth/callback",  
                    "https://flirtdecks.com",
                    "https://flirtdecks.com/callback",
                    "https://flirtdecks.com/auth/callback", 
                    "https://www.flirtdecks.com",
                    "https://www.flirtdecks.com/callback",
                    "https://www.flirtdecks.com/auth/callback" 
                ],
                
                # Logout URLs: Where Cognito redirects after logout
                logout_urls=[
                    "http://localhost:5173",
                    "https://flirtdecks.com",
                    "https://www.flirtdecks.com"
                ]
            ),
            
            # Prevent user existence errors for security
            # Returns generic error instead of "user doesn't exist"
            prevent_user_existence_errors=True
        )
        
        # Configure Google as Identity Provider
        # This allows users to "Sign in with Google"
        google_provider = cognito.UserPoolIdentityProviderGoogle(
            self,
            "GoogleProvider",
            user_pool=self.user_pool,
            
            # Google OAuth credentials from environment variables
            client_id=google_client_id,
            client_secret=google_client_secret,
            
            # Attribute mapping: Map Google profile fields to Cognito attributes
            # This tells Cognito which Google data to store
            attribute_mapping=cognito.AttributeMapping(
                email=cognito.ProviderAttribute.GOOGLE_EMAIL,
                given_name=cognito.ProviderAttribute.GOOGLE_GIVEN_NAME,
                family_name=cognito.ProviderAttribute.GOOGLE_FAMILY_NAME,
                profile_picture=cognito.ProviderAttribute.GOOGLE_PICTURE
            ),
            
            # Scopes to request from Google
            # Defines what data we want from Google
            scopes=["email", "openid", "profile"]
        )
        
        # Important: Client must depend on provider being created first
        # This ensures Google provider exists before client tries to use it
        self.user_pool_client.node.add_dependency(google_provider)
        
        # Add resource tags for cost tracking
        Tags.of(self).add("Project", "FlirtDeck")
        Tags.of(self).add("Environment", "Production")
        Tags.of(self).add("ManagedBy", "CDK")
        
        # CloudFormation Outputs
        # These values will be displayed after deployment
        # Frontend will need these to configure authentication
        
        CfnOutput(
            self,
            "UserPoolId",
            value=self.user_pool.user_pool_id,
            description="Cognito User Pool ID"
        )
        
        CfnOutput(
            self,
            "UserPoolClientId",
            value=self.user_pool_client.user_pool_client_id,
            description="Cognito User Pool Client ID"
        )
        
        CfnOutput(
            self,
            "CognitoDomain",
            value=f"{user_pool_domain.domain_name}.auth.{Stack.of(self).region}.amazoncognito.com",
            description="Cognito Hosted UI Domain"
        )
