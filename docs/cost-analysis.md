# FlirtDeck Cost Analysis

**Last Updated:** November 2025  
**Region:** us-west-2  
**Currency:** USD

---

## Executive Summary

FlirtDeck operates at approximately **$6-7/month** for 1,000 active users, scaling to **~$45/month** at 10,000 users. The serverless architecture ensures you only pay for actual usage, with no idle capacity costs.

**Key Cost Drivers:**
1. API Gateway (54% of total)
2. DynamoDB (19%)
3. Lambda (13%)
4. CloudFront/S3 (8%)
5. Other services (6%)

---

## Detailed Cost Breakdown

### 1. AWS Lambda

**Pricing Model:**
- $0.20 per 1M requests
- $0.0000166667 per GB-second of compute

**Assumptions (1,000 users):**
- 500,000 invocations/month (500 per user)
- Average 256MB memory, 200ms duration
- 4 Lambda functions (auth, questions, connections, billing)

**Monthly Cost:**
```
Requests: 500,000 × $0.20/1M = $0.10
Compute:  500,000 × 0.2s × 0.25GB × $0.0000166667 = $0.42
---------
Total:    $0.52/month
```

**At Scale (10K users):**
- 5M invocations: $5.20/month

---

### 2. DynamoDB

**Pricing Model (On-Demand):**
- Write: $1.25 per million write request units
- Read: $0.25 per million read request units
- Storage: $0.25 per GB-month

**Assumptions (1,000 users):**
- 2M read units/month (user profiles, questions, connections)
- 1M write units/month (new connections, usage tracking)
- 1 GB data stored

**Monthly Cost:**
```
Reads:    2M × $0.25/1M = $0.50
Writes:   1M × $1.25/1M = $1.25
Storage:  1 GB × $0.25  = $0.25
---------
Total:    $2.00/month
```

**At Scale (10K users):**
- 20M reads, 10M writes, 10GB: $15.00/month

---

### 3. API Gateway

**Pricing Model:**
- $3.50 per million REST API requests
- $0.09 per GB data transfer out (first 10 TB)

**Assumptions (1,000 users):**
- 1M API requests/month
- 100 MB average response size per 1K requests

**Monthly Cost:**
```
Requests: 1M × $3.50/1M     = $3.50
Data Out: 100 MB × $0.09/GB = $0.01
---------
Total:    $3.51/month
```

**At Scale (10K users):**
- 10M requests: $35.00/month

---

### 4. S3 + CloudFront

**S3 Pricing:**
- Standard storage: $0.023 per GB-month
- GET requests: $0.0004 per 1,000 requests

**CloudFront Pricing:**
- Data transfer out: $0.085 per GB (first 10 TB)
- HTTP/HTTPS requests: $0.0075 per 10,000 requests

**Assumptions:**
- 500 MB React app stored in S3
- 50% cache hit rate on CloudFront
- 100K frontend requests/month

**Monthly Cost:**
```
S3 Storage:    0.5 GB × $0.023           = $0.01
S3 Requests:   50K × $0.0004/1K          = $0.02
CF Requests:   100K × $0.0075/10K        = $0.08
CF Data Out:   50 GB × $0.085            = $4.25
---------
Total:         $4.36/month
```

**At Scale (10K users):**
- Same cost (CDN caching keeps this flat)

---

### 5. Amazon Cognito

**Pricing Model:**
- First 50,000 monthly active users (MAUs): **FREE**
- 50,001 - 100,000 MAUs: $0.0055 per MAU

**Assumptions (1,000 users):**
- All users within free tier

**Monthly Cost:** $0.00

**At Scale (60,000 users):**
- First 50K free, next 10K: $55.00/month

---

### 6. Secrets Manager

**Pricing Model:**
- $0.40 per secret per month
- $0.05 per 10,000 API calls

**Assumptions:**
- 2 secrets stored (Google OAuth, Stripe API key)
- 500K secret retrievals/month (Lambda cold starts)

**Monthly Cost:**
```
Storage:  2 × $0.40       = $0.80
API Calls: 500K × $0.05/10K = $2.50
---------
Total:    $3.30/month
```

**Optimization:** Cache secrets in Lambda memory, reduces to $1.00/month

---

### 7. CloudWatch

**Pricing Model:**
- Log ingestion: $0.50 per GB
- Log storage: $0.03 per GB-month
- Custom metrics: $0.30 per metric per month

**Assumptions:**
- 5 GB logs ingested/month
- 10 custom metrics tracked

**Monthly Cost:**
```
Ingestion: 5 GB × $0.50   = $2.50
Storage:   5 GB × $0.03   = $0.15
Metrics:   10 × $0.30     = $3.00
---------
Total:     $5.65/month
```

**Optimization:** Reduce log verbosity, aggregate metrics: $2.00/month

---

### 8. CodePipeline + CodeBuild

**Pricing Model:**
- CodePipeline: $1.00 per active pipeline per month
- CodeBuild: $0.005 per build minute (general1.small)

**Assumptions:**
- 1 active pipeline
- 20 builds/month, 5 minutes each

**Monthly Cost:**
```
Pipeline: 1 × $1.00          = $1.00
Build:    100 mins × $0.005  = $0.50
---------
Total:    $1.50/month
```

---

## Total Monthly Costs

### Small Scale (1,000 Users)
| Service | Cost |
|---------|------|
| Lambda | $0.52 |
| DynamoDB | $2.00 |
| API Gateway | $3.51 |
| S3 + CloudFront | $4.36 |
| Cognito | $0.00 |
| Secrets Manager | $3.30 |
| CloudWatch | $5.65 |
| CI/CD | $1.50 |
| **Total** | **$20.84/month** |

**After Optimizations:** ~$12/month

---

### Medium Scale (10,000 Users)
| Service | Cost |
|---------|------|
| Lambda | $5.20 |
| DynamoDB | $15.00 |
| API Gateway | $35.00 |
| S3 + CloudFront | $4.36 |
| Cognito | $0.00 |
| Secrets Manager | $1.00 |
| CloudWatch | $8.00 |
| CI/CD | $1.50 |
| **Total** | **$70.06/month** |

---

### Large Scale (100,000 Users)
| Service | Cost |
|---------|------|
| Lambda | $52.00 |
| DynamoDB | $150.00 |
| API Gateway | $350.00 |
| S3 + CloudFront | $10.00 |
| Cognito | $275.00 |
| Secrets Manager | $1.00 |
| CloudWatch | $25.00 |
| CI/CD | $1.50 |
| **Total** | **$864.50/month** |

---

## Cost Optimization Strategies

### Immediate (No Code Changes)
1. **Enable DynamoDB Auto-Scaling** - Switch from on-demand to provisioned for predictable traffic
2. **CloudWatch Log Retention** - Reduce from 30 days to 7 days ($2/month savings)
3. **S3 Lifecycle Policies** - Move old assets to Glacier ($0.50/month savings)

### Short-Term (Minor Changes)
1. **Lambda Reserved Concurrency** - For billing/auth functions ($15/month savings at scale)
2. **API Gateway Caching** - 5-minute cache for `/questions` endpoint ($10/month savings)
3. **CloudFront Cache Headers** - Increase TTL for static assets ($2/month savings)

### Long-Term (Architecture Changes)
1. **ElastiCache Redis** - Cache frequent queries, reduce DynamoDB reads 60% ($50/month savings at 100K users)
2. **Lambda@Edge** - Move auth logic to edge for faster response ($5/month increase, better UX)
3. **S3 Transfer Acceleration** - Faster uploads for user-generated content (TBD cost)

---

## Revenue Model

**Free Tier:**
- 10 questions per day
- Basic connection tracking
- **Target:** 90% of users

**Premium ($2.99/month):**
- Unlimited questions
- Advanced analytics
- Priority support
- **Target:** 10% conversion rate

**Break-Even Analysis:**
- Cost at 1,000 users: $12/month (after optimization)
- Revenue per premium user after Stripe fees: $2.99 - ($2.99 × 2.9% + $0.30) = **$2.60/month**
- Premium users needed: $12 ÷ $2.60 = **5 subscribers**
- **Break-even: 50 total users** (assuming 10% conversion)

**Profitability at Scale:**
- 1,000 users @ 10% conversion = 100 premium subscribers
  - Revenue: 100 × $2.99 = **$299/month**
  - Stripe fees: 100 × ($2.99 × 2.9% + $0.30) = **$38.68/month**
  - Net revenue: $299 - $38.68 = **$260.32/month**
  - Cost: $12/month
  - **Profit: $248.32/month (95.4% margin)**

- 10,000 users @ 10% conversion = 1,000 premium subscribers
  - Revenue: 1,000 × $2.99 = **$2,990/month**
  - Stripe fees: 1,000 × ($2.99 × 2.9% + $0.30) = **$386.71/month**
  - Net revenue: $2,990 - $386.71 = **$2,603.29/month**
  - Cost: $70/month
  - **Profit: $2,533.29/month (97.3% margin)**

- 100,000 users @ 10% conversion = 10,000 premium subscribers
  - Revenue: 10,000 × $2.99 = **$29,900/month**
  - Stripe fees: 10,000 × ($2.99 × 2.9% + $0.30) = **$3,867.10/month**
  - Net revenue: $29,900 - $3,867.10 = **$26,032.90/month**
  - Cost: $865/month
  - **Profit: $25,167.90/month (96.7% margin)**

**Note:** Stripe charges 2.9% + $0.30 per successful transaction

---

## Cost Monitoring

**CloudWatch Alarms Set:**
- DynamoDB consumed capacity > $5/day
- Lambda invocation errors > 1%
- API Gateway 4xx rate > 10%
- Unexpected S3 data transfer > 100 GB/day

**Monthly Budget Alert:** $50 threshold

**Cost Allocation Tags:**
```
Project: FlirtDeck
Environment: Production
Owner: DevOps
CostCenter: Engineering
```

---

## Conclusion

FlirtDeck's serverless architecture keeps costs extremely low while maintaining high availability and performance. The pay-per-use model ensures you only pay for actual traffic, making it ideal for a portfolio project or MVP.

**Total 1st Year Cost (projected):**
- Months 1-3 (development): $5/month × 3 = $15
- Months 4-12 (1,000 users): $12/month × 9 = $108
- **Total: $123/year**

**ROI at 200 users with 10% premium conversion:**
- Premium users: 200 × 10% = 20 subscribers
- Gross revenue: 20 × $2.99 × 12 = **$718/year**
- Stripe fees: 20 × 12 × ($2.99 × 2.9% + $0.30) = **$93.24/year**
- Net revenue: $718 - $93.24 = **$624.76/year**
- Costs: $12 × 12 = **$144/year**
- **Net profit: $480.76/year (334% ROI)**

**Conservative Scenario (100 users, 5% conversion):**
- Premium users: 100 × 5% = 5 subscribers
- Gross revenue: 5 × $2.99 × 12 = **$179.40/year**
- Stripe fees: 5 × 12 × ($2.99 × 2.9% + $0.30) = **$23.31/year**
- Net revenue: $179.40 - $23.31 = **$156.09/year**
- Costs: $10 × 12 = **$120/year**
- **Net profit: $36.09/year (30% ROI)**

**Aggressive Scenario (1,000 users, 15% conversion):**
- Premium users: 1,000 × 15% = 150 subscribers
- Gross revenue: 150 × $2.99 × 12 = **$5,382/year**
- Stripe fees: 150 × 12 × ($2.99 × 2.9% + $0.30) = **$699.48/year**
- Net revenue: $5,382 - $699.48 = **$4,682.52/year**
- Costs: $12 × 12 = **$144/year**
- **Net profit: $4,538.52/year (3,152% ROI)**