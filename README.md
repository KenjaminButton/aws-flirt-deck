# FlirtDeck - AWS Portfolio Project

Multi-tenant SaaS application for dating conversation assistance.

## Tech Stack
- **Backend:** Python, AWS CDK, Lambda, DynamoDB, API Gateway
- **Frontend:** React, TypeScript, Vite, Tailwind CSS
- **Auth:** Amazon Cognito with Google OAuth
- **Billing:** Stripe
- **Region:** us-west-2

## Status
🚧 Under Development

## Documentation
Coming soon...



### Notes: 

```json
// CDK tags planning for a later phase
tags = {
    "Project": "FlirtDeck",
    "Environment": "Production",
    "ManagedBy": "CDK"
}
```


**Tasks:**
- [x] Create `infrastructure/infrastructure/cognito_stack.py`:
  - User Pool with email sign-in
  - Password policy (min 8 chars, uppercase, lowercase, digit)
  - Cognito domain: `flirtdeck-dev` (must be globally unique - add random suffix if needed)
  - User Pool Client (no secret, OAuth flows enabled)
  - Google Identity Provider (use credentials from Day 2)
  - Callback URLs: localhost (will add CloudFront later)
  - Scopes: email, openid, profile
- [x] Update `app.py` to deploy CognitoStack
- [x] Pass Google credentials via environment variables

**Commands:**
```bash
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-secret"
cdk deploy CognitoStack
```

**Verification:**
- [x] Cognito User Pool created
- [x] Check AWS Console: Cognito → User Pools
- [x] Google provider configured under "Sign-in experience" → "Federated identity providers"
- [x] Copy Cognito domain from outputs (e.g., `flirtdeck-dev.auth.us-west-2.amazoncognito.com`)