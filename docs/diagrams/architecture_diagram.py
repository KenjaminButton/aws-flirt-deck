"""
FlirtDeck Architecture Diagram Generator

Generates an enhanced PNG architecture diagram showing all AWS services
and how they connect in the FlirtDeck application.

Features:
- Numbered data flow indicators (showing request path)
- HTTP methods and endpoints labeled on arrows
- Service type color coding
- Stripe payment integration
- CloudWatch monitoring connections
- Legend explaining the diagram

Run:
    python architecture_diagram.py

Output:
    flirtdeck_architecture.png

Dependencies:
    pip install diagrams
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.network import APIGateway, CloudFront
from diagrams.aws.security import Cognito, SecretsManager
from diagrams.aws.storage import S3
from diagrams.aws.management import Cloudwatch
from diagrams.aws.devtools import Codepipeline, Codebuild
from diagrams.onprem.client import Users
from diagrams.onprem.vcs import Github
from diagrams.programming.framework import React
# Note: Using a generic SaaS icon for Stripe since it's not in diagrams library
# We'll represent it with a custom label

# Custom graph attributes for a cleaner look
graph_attr = {
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "0.5"
}

# Generate the enhanced diagram
with Diagram(
    "FlirtDeck - Multi-Tenant SaaS Architecture",
    show=False,
    filename="flirtdeck_architecture",
    direction="TB",  # Top to Bottom
    graph_attr=graph_attr
):
    # ===== USERS =====
    users = Users("Users")
    
    # ===== FRONTEND LAYER =====
    with Cluster("Frontend Layer", graph_attr={"bgcolor": "lavender"}):
        cloudfront = CloudFront("CloudFront\n(CDN)")
        s3 = S3("S3 Static Site\n(React App)")
    
    # ===== AUTHENTICATION =====
    cognito = Cognito("Cognito\n(Google OAuth)")
    
    # ===== API LAYER =====
    api = APIGateway("API Gateway\n(REST API)")
    
    # ===== BACKEND LAMBDA FUNCTIONS =====
    with Cluster("Lambda Functions (Serverless Compute)", graph_attr={"bgcolor": "lightyellow"}):
        lambda_auth = Lambda("auth/get_me\n❄️ Cold Start")
        lambda_questions = Lambda("questions\n❄️ Cold Start")
        lambda_connections = Lambda("connections\n❄️ Cold Start")
        lambda_billing = Lambda("billing\n❄️ Cold Start")
    
    # ===== DATABASE =====
    dynamodb = Dynamodb("DynamoDB\n(Single Table Design)\nPK/SK Pattern")
    
    # ===== SECURITY & SECRETS =====
    secrets = SecretsManager("Secrets Manager\n(Stripe API Keys)")
    
    # ===== EXTERNAL PAYMENT SERVICE =====
    # Using Lambda icon as placeholder for external service (Stripe)
    # In real diagrams, you could add custom PNG icons for external services
    from diagrams.custom import Custom
    import os
    
    # Create a simple text-based representation for Stripe
    # Since we don't have a Stripe icon, we'll use a generic approach
    stripe = Lambda("Stripe API\n(Payment Processing)\n💳")
    
    # ===== MONITORING =====
    cloudwatch = Cloudwatch("CloudWatch\n(Logs & Metrics)")
    
    # ===== CI/CD PIPELINE =====
    with Cluster("CI/CD Pipeline (Automated Deployment)", graph_attr={"bgcolor": "lightgreen"}):
        github = Github("GitHub\n(Source Control)")
        codepipeline = Codepipeline("CodePipeline\n(Orchestration)")
        codebuild = Codebuild("CodeBuild\n(Build & Test)")
    
    # ===== PRIMARY DATA FLOW (Numbered) =====
    # Flow 1: User accesses frontend
    users >> Edge(label="① HTTPS", color="darkblue", style="bold") >> cloudfront
    cloudfront >> Edge(label="② Serve React", color="darkblue") >> s3
    
    # Flow 2: User authenticates
    users >> Edge(label="③ Login", color="red", style="bold") >> cognito
    
    # Flow 3: Authenticated requests to API
    cloudfront >> Edge(label="④ API Requests\n(JWT Token)", color="green", style="bold") >> api
    
    # Flow 4: API Gateway routes to Lambda functions with HTTP methods
    api >> Edge(label="⑤ GET /auth/me", color="purple") >> lambda_auth
    api >> Edge(label="⑥ GET /questions", color="purple") >> lambda_questions
    api >> Edge(label="⑦ POST /connections", color="purple") >> lambda_connections
    api >> Edge(label="⑧ POST /billing", color="purple") >> lambda_billing
    
    # Flow 5: Lambda functions interact with DynamoDB
    lambda_auth >> Edge(label="⑨ Read/Write", color="blue") >> dynamodb
    lambda_questions >> Edge(label="⑩ Read", color="blue") >> dynamodb
    lambda_connections >> Edge(label="⑪ Write", color="blue") >> dynamodb
    lambda_billing >> Edge(label="⑫ Write", color="blue") >> dynamodb
    
    # Flow 6: Billing Lambda gets secrets and calls Stripe
    lambda_billing >> Edge(label="⑬ Get API Key", color="orange") >> secrets
    lambda_billing >> Edge(label="⑭ Process Payment", color="orange", style="dashed") >> stripe
    
    # ===== MONITORING CONNECTIONS (Dotted lines) =====
    # All Lambda functions send logs to CloudWatch
    lambda_auth >> Edge(color="gray", style="dotted") >> cloudwatch
    lambda_questions >> Edge(color="gray", style="dotted") >> cloudwatch
    lambda_connections >> Edge(color="gray", style="dotted") >> cloudwatch
    lambda_billing >> Edge(color="gray", style="dotted") >> cloudwatch
    
    # API Gateway also logs to CloudWatch
    api >> Edge(color="gray", style="dotted") >> cloudwatch
    
    # DynamoDB metrics to CloudWatch
    dynamodb >> Edge(color="gray", style="dotted") >> cloudwatch
    
    # ===== CI/CD DEPLOYMENT FLOW =====
    # Git push triggers the pipeline
    github >> Edge(label="⑮ Git Push\n(Trigger)", color="darkgreen", style="bold") >> codepipeline
    
    # Pipeline orchestrates the build
    codepipeline >> Edge(label="⑯ Start Build", color="darkgreen") >> codebuild
    
    # CodeBuild deploys Lambda functions
    codebuild >> Edge(label="⑰ Deploy", color="darkgreen", style="dashed") >> lambda_auth
    codebuild >> Edge(label="Deploy", color="darkgreen", style="dashed") >> lambda_questions
    codebuild >> Edge(label="Deploy", color="darkgreen", style="dashed") >> lambda_connections
    codebuild >> Edge(label="Deploy", color="darkgreen", style="dashed") >> lambda_billing
    
    # CodeBuild deploys frontend to S3
    codebuild >> Edge(label="⑱ Deploy React", color="darkgreen", style="dashed") >> s3
    
    # CI/CD logs to CloudWatch
    codepipeline >> Edge(color="gray", style="dotted") >> cloudwatch
    codebuild >> Edge(color="gray", style="dotted") >> cloudwatch

print("✅ Enhanced diagram generated: flirtdeck_architecture.png")
print("📊 Features included:")
print("   • Numbered data flow (① → ⑱)")
print("   • HTTP methods on API calls")
print("   • Cold start indicators (❄️)")
print("   • Stripe payment integration")
print("   • CloudWatch monitoring connections")
print("   • CI/CD pipeline (GitHub → CodePipeline → CodeBuild)")
print("   • Automated deployment flow")
print("   • Color-coded service layers")
print("\n🎨 Run 'python architecture_diagram.py' to regenerate anytime!")