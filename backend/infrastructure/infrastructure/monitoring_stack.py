"""
Monitoring Stack: CloudWatch Dashboard for FlirtDeck

Creates a dashboard to monitor:
- API Gateway request metrics
- Lambda function performance
- DynamoDB usage

This is your "mission control" to see how your app is performing.
"""

from aws_cdk import (
    Stack,
    Duration,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cloudwatch_actions,
)
from constructs import Construct


class MonitoringStack(Stack):
    """
    Monitoring Stack - CloudWatch Dashboard
    
    Think of this as your app's health dashboard, like a car's instrument panel
    showing speed, fuel, engine temp, etc.
    """
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Import SNS modules
        from aws_cdk import aws_sns as sns
        from aws_cdk import aws_sns_subscriptions as sns_subs
        
        # Create SNS Topic for alarm notifications
        alarm_topic = sns.Topic(
            self,
            "AlarmTopic",
            topic_name="flirtdeck-alarms",
            display_name="FlirtDeck Alarm Notifications"
        )
        
        # Subscribe your email (REPLACE WITH YOUR ACTUAL EMAIL)
        alarm_topic.add_subscription(
            sns_subs.EmailSubscription("kennethpchang@gmail.com")
        )


        # Create CloudWatch Dashboard
        dashboard = cloudwatch.Dashboard(
            self,
            "FlirtDeckDashboard",
            dashboard_name="FlirtDeck-Metrics"
        )
        
        # API Gateway Metrics
        # Shows: How many requests? Any errors? How fast?
        api_widget = cloudwatch.GraphWidget(
            title="API Gateway Requests",
            left=[
                # Total request count
                cloudwatch.Metric(
                    namespace="AWS/ApiGateway",
                    metric_name="Count",
                    dimensions_map={
                        "ApiName": "flirtdeck-api"
                    },
                    statistic="Sum",
                    period=Duration.minutes(5),
                    label="Total Requests"
                ),
                # 4XX errors (client errors - bad requests)
                cloudwatch.Metric(
                    namespace="AWS/ApiGateway",
                    metric_name="4XXError",
                    dimensions_map={
                        "ApiName": "flirtdeck-api"
                    },
                    statistic="Sum",
                    period=Duration.minutes(5),
                    label="4XX Errors",
                    color=cloudwatch.Color.ORANGE
                ),
                # 5XX errors (server errors - our fault)
                cloudwatch.Metric(
                    namespace="AWS/ApiGateway",
                    metric_name="5XXError",
                    dimensions_map={
                        "ApiName": "flirtdeck-api"
                    },
                    statistic="Sum",
                    period=Duration.minutes(5),
                    label="5XX Errors",
                    color=cloudwatch.Color.RED
                )
            ],
            width=12,
            height=6
        )
        
        # Lambda Metrics Widget
        lambda_widget = cloudwatch.GraphWidget(
            title="Lambda: GetMe Function",
            left=[
                cloudwatch.Metric(
                    namespace="AWS/Lambda",
                    metric_name="Invocations",
                    dimensions_map={"FunctionName": "ApiStack-GetMeFunction883856F2-7eJdlsSQ7BR8"},
                    statistic="Sum",
                    period=Duration.minutes(5),
                    label="Invocations"
                ),
                cloudwatch.Metric(
                    namespace="AWS/Lambda",
                    metric_name="Errors",
                    dimensions_map={"FunctionName": "ApiStack-GetMeFunction883856F2-7eJdlsSQ7BR8"},
                    statistic="Sum",
                    period=Duration.minutes(5),
                    label="Errors",
                    color=cloudwatch.Color.RED
                ),
                cloudwatch.Metric(
                    namespace="AWS/Lambda",
                    metric_name="Throttles",
                    dimensions_map={"FunctionName": "ApiStack-GetMeFunction883856F2-7eJdlsSQ7BR8"},
                    statistic="Sum",
                    period=Duration.minutes(5),
                    label="Throttles",
                    color=cloudwatch.Color.ORANGE
                )
            ],
            right=[
                cloudwatch.Metric(
                    namespace="AWS/Lambda",
                    metric_name="Duration",
                    dimensions_map={"FunctionName": "ApiStack-GetMeFunction883856F2-7eJdlsSQ7BR8"},
                    statistic="Average",
                    period=Duration.minutes(5),
                    label="Avg Duration (ms)"
                )
            ],
            width=12,
            height=6
        )

        # DynamoDB Metrics Widget
        dynamodb_widget = cloudwatch.GraphWidget(
            title="DynamoDB: flirtdeck-table",
            left=[
                cloudwatch.Metric(
                    namespace="AWS/DynamoDB",
                    metric_name="ConsumedReadCapacityUnits",
                    dimensions_map={"TableName": "flirtdeck-table"},
                    statistic="Sum",
                    period=Duration.minutes(5),
                    label="Read Capacity"
                ),
                cloudwatch.Metric(
                    namespace="AWS/DynamoDB",
                    metric_name="ConsumedWriteCapacityUnits",
                    dimensions_map={"TableName": "flirtdeck-table"},
                    statistic="Sum",
                    period=Duration.minutes(5),
                    label="Write Capacity"
                )
            ],
            right=[
                cloudwatch.Metric(
                    namespace="AWS/DynamoDB",
                    metric_name="UserErrors",
                    dimensions_map={"TableName": "flirtdeck-table"},
                    statistic="Sum",
                    period=Duration.minutes(5),
                    label="Throttled Requests",
                    color=cloudwatch.Color.RED
                )
            ],
            width=12,
            height=6
        )

        # API Latency Widget
        latency_widget = cloudwatch.GraphWidget(
            title="API Response Time (Latency)",
            left=[
                cloudwatch.Metric(
                    namespace="AWS/ApiGateway",
                    metric_name="Latency",
                    dimensions_map={"ApiName": "flirtdeck-api"},
                    statistic="p50",
                    period=Duration.minutes(5),
                    label="p50 (median)"
                ),
                cloudwatch.Metric(
                    namespace="AWS/ApiGateway",
                    metric_name="Latency",
                    dimensions_map={"ApiName": "flirtdeck-api"},
                    statistic="p95",
                    period=Duration.minutes(5),
                    label="p95",
                    color=cloudwatch.Color.ORANGE
                ),
                cloudwatch.Metric(
                    namespace="AWS/ApiGateway",
                    metric_name="Latency",
                    dimensions_map={"ApiName": "flirtdeck-api"},
                    statistic="p99",
                    period=Duration.minutes(5),
                    label="p99 (worst case)",
                    color=cloudwatch.Color.RED
                )
            ],
            width=12,
            height=6
        )

        # CloudWatch Alarms
        # Alarm 1: API Gateway 5XX Errors
        api_5xx_alarm = cloudwatch.Alarm(
            self,
            "Api5XXErrorAlarm",
            alarm_name="FlirtDeck-API-5XX-Errors",
            alarm_description="Alert when API returns server errors",
            metric=cloudwatch.Metric(
                namespace="AWS/ApiGateway",
                metric_name="5XXError",
                dimensions_map={"ApiName": "flirtdeck-api"},
                statistic="Sum",
                period=Duration.minutes(5)
            ),
            threshold=5,  # Alert if >5 errors in 5 minutes
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
        )
        api_5xx_alarm.add_alarm_action(cloudwatch_actions.SnsAction(alarm_topic))
        
        # Alarm 2: Lambda Errors
        lambda_error_alarm = cloudwatch.Alarm(
            self,
            "LambdaErrorAlarm",
            alarm_name="FlirtDeck-Lambda-Errors",
            alarm_description="Alert when Lambda functions fail",
            metric=cloudwatch.Metric(
                namespace="AWS/Lambda",
                metric_name="Errors",
                dimensions_map={"FunctionName": "ApiStack-GetMeFunction883856F2-7eJdlsSQ7BR8"},
                statistic="Sum",
                period=Duration.minutes(5)
            ),
            threshold=10,  # Alert if >10 errors in 5 minutes
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
        )
        lambda_error_alarm.add_alarm_action(cloudwatch_actions.SnsAction(alarm_topic))

        # Add widgets to dashboard
        dashboard.add_widgets(api_widget, lambda_widget, dynamodb_widget, latency_widget)
