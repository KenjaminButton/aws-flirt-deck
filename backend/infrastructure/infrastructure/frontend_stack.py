"""
Frontend Stack: S3 + CloudFront for React app hosting

This stack creates:
- S3 bucket for static website hosting
- CloudFront distribution for global CDN
- Origin Access Identity (OAI) for secure S3 access
- Custom error responses for SPA routing
"""

from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3_deployment as s3deploy,
    aws_certificatemanager as acm,
    RemovalPolicy,
    CfnOutput,
    Duration,
    Tags
)
from constructs import Construct
import os


class FrontendStack(Stack):
    """
    FrontendStack: Deploys React frontend to S3 with CloudFront
    
    Creates a production-ready hosting setup with:
    - S3 bucket (private, not public)
    - CloudFront distribution (HTTPS, global CDN)
    - OAI (only CloudFront can access S3)
    - SPA routing support (404 → index.html)
    """
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create S3 bucket for website hosting
        # Bucket is PRIVATE - only CloudFront can access it via OAI
        self.website_bucket = s3.Bucket(
            self,
            "FlirtDeckWebsiteBucket",
            bucket_name=f"flirtdeck-frontend-{self.account}",  # Must be globally unique
            
            # Block all public access (CloudFront will access via OAI)
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            
            # DESTROY: Deletes bucket when stack is deleted (good for dev/demo)
            # For production, consider RETAIN
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,  # Delete objects when stack is destroyed
            
            # Enable versioning for rollback capability
            versioned=False,  # Set to True for production if you want version history
            
            # Encryption at rest
            encryption=s3.BucketEncryption.S3_MANAGED
        )
        
        # Create Origin Access Identity (OAI)
        # This allows CloudFront to access the private S3 bucket
        oai = cloudfront.OriginAccessIdentity(
            self,
            "FlirtDeckOAI",
            comment="OAI for FlirtDeck frontend"
        )
        
        # Grant CloudFront read access to S3 bucket
        self.website_bucket.grant_read(oai)
        
        # Create CloudFront distribution
        self.distribution = cloudfront.Distribution(
            self,
            "FlirtDeckDistribution",
            
            # Custom domain names and SSL certificate
            domain_names=["flirtdecks.com", "www.flirtdecks.com"],
            certificate=acm.Certificate.from_certificate_arn(
                self,
                "Certificate",
                certificate_arn="arn:aws:acm:us-east-1:811230534980:certificate/6676ab09-6ff1-4432-8a4f-0139d1d3a7cb"
            ),

            # S3 origin with OAI
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(
                    self.website_bucket,
                    origin_access_identity=oai
                ),
                
                # Viewer protocol: Redirect HTTP to HTTPS
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                
                # Cache policy: Optimize for SPA
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                
                # Allowed HTTP methods
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
                
                # Compress text files automatically
                compress=True
            ),
            


            # Default root object
            default_root_object="index.html",
            
            # Custom error responses for SPA routing
            # When user navigates to /connections or /questions, CloudFront returns index.html
            # React Router handles the actual routing
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.minutes(5)
                ),
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.minutes(5)
                )
            ],
            
            # Price class: Use only North America and Europe (cheaper)
            # For global: cloudfront.PriceClass.PRICE_CLASS_ALL
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,
            
            # Enable IPv6
            enable_ipv6=True,
            
            # HTTP version
            http_version=cloudfront.HttpVersion.HTTP2_AND_3,
            
            # Minimum TLS version
            minimum_protocol_version=cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021
        )
        
        # Add resource tags
        Tags.of(self).add("Project", "FlirtDeck")
        Tags.of(self).add("Environment", "Production")
        Tags.of(self).add("ManagedBy", "CDK")
        
        # CloudFormation Outputs
        # These values are needed for deployment and configuration
        
        CfnOutput(
            self,
            "WebsiteBucketName",
            value=self.website_bucket.bucket_name,
            description="S3 bucket name for website files",
            export_name="FlirtDeckWebsiteBucket"
        )
        
        CfnOutput(
            self,
            "DistributionId",
            value=self.distribution.distribution_id,
            description="CloudFront distribution ID",
            export_name="FlirtDeckDistributionId"
        )
        
        CfnOutput(
            self,
            "DistributionDomainName",
            value=self.distribution.distribution_domain_name,
            description="CloudFront domain name (your app URL)",
            export_name="FlirtDeckDistributionDomain"
        )
        
        CfnOutput(
            self,
            "WebsiteURL",
            value=f"https://{self.distribution.distribution_domain_name}",
            description="Full HTTPS URL for your app",
            export_name="FlirtDeckWebsiteURL"
        )
