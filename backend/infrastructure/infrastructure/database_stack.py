from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    RemovalPolicy,
    Tags
)
from constructs import Construct


class DatabaseStack(Stack):
    """
    DatabaseStack: Creates the DynamoDB table for FlirtDeck
    
    This stack implements a single-table design pattern for multi-tenant data:
    - Main table with PK/SK for flexible entity modeling
    - GSI1 for alternate query patterns
    - On-demand billing to minimize costs
    """
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create the main DynamoDB table
        # Single-table design: all entities (users, connections, questions) in one table
        self.table = dynamodb.Table(
            self,
            "FlirtDeckTable",  # Logical ID in CloudFormation
            table_name="flirtdeck-table",  # Actual table name in AWS
            
            # Primary key structure for single-table design
            # PK examples: USER#123, QUESTION#456
            # SK examples: PROFILE, CONNECTION#789, USAGE#2024-01-15
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="SK",
                type=dynamodb.AttributeType.STRING
            ),
            
            # PAY_PER_REQUEST = on-demand billing
            # Only pay for actual reads/writes, no minimum cost
            # Perfect for unpredictable traffic patterns
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            
            # Point-in-time recovery: allows restoring table to any point in last 35 days
            # Protects against accidental deletions or data corruption
            point_in_time_recovery=True,
            
            # DESTROY: table deleted when stack is deleted (good for dev)
            # For production, you'd use RETAIN to prevent accidental data loss
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Add Global Secondary Index (GSI1)
        # GSIs allow querying the table using different key attributes
        # Use case: Query connections by category, or questions by type
        # GSI1PK example: CATEGORY#flirty, USER#123#CONNECTIONS
        # GSI1SK example: QUESTION#789, CONNECTION#456
        self.table.add_global_secondary_index(
            index_name="GSI1",
            partition_key=dynamodb.Attribute(
                name="GSI1PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="GSI1SK",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        # Add resource tags for cost tracking and organization
        # These tags will appear in AWS Cost Explorer
        # Allows filtering bills by project, environment, etc.
        Tags.of(self).add("Project", "FlirtDeck")
        Tags.of(self).add("Environment", "Production")
        Tags.of(self).add("ManagedBy", "CDK")