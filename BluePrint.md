## Multi-Tenant SaaS with CI/CD & Full Observability
# FlirtDeck - Complete AWS Portfolio Project Blueprint

---

## 🎯 Project Goal

Build a production-ready, multi-tenant SaaS application showcasing:
- Modern AWS serverless architecture
- OAuth 2.0 authentication
- Payment integration (Stripe)
- Infrastructure as Code (Python CDK)
- Full CI/CD pipeline
- Production observability (monitoring, alerting, dashboards)

**Timeline:** 25-30 days (3-4 hours/day) or 3 weeks full-time
**Region:** us-west-2
**Cost:** $5-10/month

---

## 📊 What This Demonstrates to Recruiters

### AWS Services (11 total):
1. **Cognito** - OAuth 2.0 with Google
2. **API Gateway** - RESTful API with authorization
3. **Lambda** - Serverless compute
4. **DynamoDB** - NoSQL single-table design
5. **S3** - Static hosting
6. **CloudFront** - CDN
7. **Secrets Manager** - Credential management
8. **CloudWatch** - Logs, metrics, alarms, dashboards
9. **IAM** - Least-privilege security
10. **CodePipeline** - CI/CD automation
11. **CodeBuild** - Build automation

### Skills Showcased:
- ✅ Full-stack development (Python + TypeScript/React)
- ✅ Infrastructure as Code (CDK)
- ✅ CI/CD pipeline implementation
- ✅ Multi-tenant architecture
- ✅ Security best practices
- ✅ Payment integration
- ✅ Production monitoring
- ✅ Cost optimization
- ✅ Documentation

**Recruiter Appeal: 9/10**

---

## 🏗️ Architecture Overview

### High-Level Flow:
```
User → CloudFront → S3 (Frontend)
User → API Gateway → Lambda → DynamoDB
User → Cognito (Google OAuth)
Lambda → Stripe API (Billing)
Lambda → Secrets Manager (API Keys)
All → CloudWatch (Logs + Metrics)
GitHub Push → CodePipeline → CodeBuild → Deploy
```

### Core Entities:
```
USER (you)
  └── CONNECTIONS (Sarah, Mike, etc. - just names, NOT users)
        └── QUESTION_USAGE (notes about what they said)

QUESTIONS (hardcoded 250 questions)
```

---

## 🎮 User Flow

### First Time User:
1. Clicks "Sign in with Google"
2. Approves Google permissions
3. Redirected to app (profile auto-created)
4. Sees 4 category buttons: Life, Random, Deep, Experiences
5. Clicks "Deep" → Gets random Deep question
6. "Use this question" → Prompted to create connection
7. Names connection: "Sarah from Hinge"
8. Logs: What Sarah said, What I said
9. Tries to create 2nd connection → Paywall: "Upgrade to Premium $2.99/mo"

### Premium User:
10. Clicks "Upgrade" → Stripe checkout
11. Pays with test card
12. Now can create unlimited connections
13. Can view history: All questions used with Sarah

---

## 📋 Prerequisites Checklist

### Accounts Needed (All Free):
- [x] AWS Account (with admin/PowerUser IAM user)
- [x] GitHub Account
- [x] Google Cloud Console Account
- [ ] Stripe Account (test mode)

### Local Tools Required:
- [x] Python 3.9+ installed (`python3 --version`)
- [x] Node.js 18+ installed (`node --version`)
- [x] AWS CLI installed & configured (`aws sts get-caller-identity`)
- [x] CDK installed globally (`npm install -g aws-cdk`)
- [x] Git installed (`git --version`)
- [x] Code editor (VS Code recommended)

### AWS Setup:
```bash
# Configure AWS CLI
aws configure
# Region: us-west-2
# Output: json

# Bootstrap CDK (one-time per account/region)
cdk bootstrap aws://ACCOUNT-ID/us-west-2
```

### Billing Protection:
- [x] Set up AWS Budget: $20/month threshold with email alert
- [x] Enable cost explorer
- [x] Tag all resources: Project=FlirtDeck

---

## 📁 Project Structure


```
flirtdeck/
├── .github/
│   └── workflows/
│       ├── backend-deploy.yml        # CI/CD for backend
│       └── frontend-deploy.yml       # CI/CD for frontend
├── backend/
│   ├── infrastructure/               # CDK app & stacks (do not change api_stack packaging)
│   │   ├── infrastructure/
│   │   │   └── api_stack.py
│   │   └── app.py
│   └── lambda_functions/             # CDK packages this entire folder for Lambdas
│       ├── shared/                   # ← Shared utilities live here
│       │   ├── responses.py
│       │   ├── dynamodb.py
│       │   └── questions_data.py     # 170 questions hardcoded
│       ├── auth/
│       │   └── get_me.py
│       └── questions/
│           └── get_random.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── context/
│   │   ├── api/
│   │   └── types/
│   ├── public/
│   └── package.json
├── docs/
│   ├── architecture.png
│   └── cost-analysis.md
├── .gitignore
└── README.md

```

Lambda packaging: CDK packages entire lambda_functions/ folder
Handler format: auth.get_me.handler or questions.get_random.handler
Imports in Lambda files: from shared.responses import ...

NEVER change api_stack.py Lambda packaging without asking first.


---

## 🚀 Implementation Roadmap

---

### **PHASE 0: Setup & Google OAuth** (Days 1-2) 🟢

#### Day 1: Repository & Environment Setup

**Tasks:**
- [x] Create GitHub repo: `flirtdeck-aws-portfolio`
- [x] Clone locally and create folder structure (see above)
- [x] Create `.gitignore` (Python, Node, CDK, secrets)
- [x] Create `credentials.txt` in backend (add to .gitignore)
- [x] Initial commit to GitHub

**Verification:**
- [x] Git repo initialized and pushed to GitHub
- [x] Folder structure matches above
- [x] `.gitignore` prevents sensitive files

---

#### Day 2: Google OAuth Setup

**Tasks:**
- [x] Go to https://console.cloud.google.com/
- [x] Create project: "FlirtDeck"
- [x] Enable Google+ API
- [x] Configure OAuth consent screen (External, add your email)
- [x] Create OAuth credentials (Web application)
- [x] Add temporary redirect URIs:
  - `http://localhost:5173/auth/callback`
  - `http://localhost:3000/auth/callback`
- [x] Save Client ID and Client Secret to `backend/credentials.txt`

**Verification:**
- [x] Google OAuth app created
- [x] Credentials saved securely
- [x] Consent screen configured

**⚠️ Trouble Spot:** Make sure you select the correct project before creating credentials.

---

### **PHASE 1: Infrastructure Foundation** (Days 3-7) 🔴

#### Day 3: DynamoDB Setup

**Tasks:**
- [x] Initialize CDK project: `cd backend/infrastructure && cdk init app --language python`
- [x] Install dependencies: `pip install -r requirements.txt boto3`
- [x] Create `infrastructure/database_stack.py`:
  - DynamoDB table: `flirtdeck-table`
  - PK: string, SK: string
  - Billing: ON_DEMAND
  - GSI: GSI1 (GSI1PK, GSI1SK)
  - Point-in-time recovery: enabled
- [x] Update `app.py` to import and deploy DatabaseStack

**Commands:**
```bash
cd backend/infrastructure
export AWS_REGION=us-west-2
cdk synth
cdk deploy DatabaseStack
```

**Verification:**
- [x] DynamoDB table created in us-west-2
- [x] Check AWS Console: DynamoDB → Tables
- [x] Table has GSI1 index

**⚠️ Trouble Spot:** If CDK bootstrap fails, run: `cdk bootstrap aws://ACCOUNT-ID/us-west-2`

---

#### Day 4: Cognito Setup

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

**⚠️ MAJOR Trouble Spot:** This is the hardest part. Common issues:
- Cognito domain already taken → Add random suffix
- Google provider not showing → Check client ID/secret are correct
- Budget 2-3 hours for debugging

---

#### Day 5: Update Google OAuth Redirect URIs

**Tasks:**
- [x] Go back to Google Cloud Console
- [x] APIs & Services → Credentials → Your OAuth client
- [x] Add new redirect URI:
```
  https://flirtdeck-dev.auth.us-west-2.amazoncognito.com/oauth2/idpresponse
```
  (Use YOUR actual Cognito domain from Day 4)
- [x] Keep localhost URIs
- [x] Save

**Verification:**
- [x] Google has Cognito redirect URI
- [x] Total of 3 redirect URIs (2 localhost + 1 Cognito)

---

#### Day 6-7: API Gateway & Lambda Base

**Tasks:**
- [x] Create `stacks/api_stack.py`:
  - REST API: `flirtdeck-api`
  - CORS enabled (localhost origins)
  - Cognito authorizer
  - Lambda execution role with DynamoDB permissions
  - Helper method to create Lambda functions
- [x] Create first Lambda: `lambda_functions/auth/get_me.py`
  - Extract user ID from Cognito JWT
  - Check if user profile exists in DynamoDB
  - If not, create profile (first Google login)
  - Return user data
- [x] Create shared utilities:
  - `shared/responses.py` (success/error response helpers)
  - `shared/dynamodb.py` (get_user_profile, create_user_profile)
- [x] Add route: `GET /auth/me` (requires auth)
- [x] Deploy

**Commands:**
```bash
cdk deploy ApiStack
```

**Verification:**
- [x] API Gateway created with `/auth/me` endpoint
- [x] Copy API URL from outputs
- [x] Check AWS Console: API Gateway → APIs → flirtdeck-api
- [x] Lambda function deployed

**Test with curl (will fail without token - expected):**
```bash
curl https://YOUR-API-URL/prod/auth/me
# Should return: {"message":"Unauthorized"}
```

**⚠️ Trouble Spot:** Make sure Lambda has DynamoDB permissions via IAM role.

---

### **PHASE 2: Authentication** (Days 8-10) 🟡

#### Day 8: Frontend Setup

**Tasks:**
- [x] Initialize React app: `cd frontend && npm create vite@latest . -- --template react-ts`
- [x] Install dependencies:
```bash
  npm install react-router-dom axios
  npm install -D tailwindcss@3 postcss autoprefixer # Make sure it is version 3, not 4. 
  npx tailwindcss init -p
```
- [x] Configure Tailwind in `tailwind.config.js`
- [x] Create `.env.local` with:
```
  VITE_API_URL=https://your-api-url/prod
  VITE_COGNITO_USER_POOL_ID=us-west-2_xxxxx
  VITE_COGNITO_CLIENT_ID=xxxxxxxxxxxxx
  VITE_COGNITO_DOMAIN=flirtdeck-dev.auth.us-west-2.amazoncognito.com
  VITE_REDIRECT_URI=http://localhost:5173/auth/callback
```
- [x] Create TypeScript types: `src/types/index.ts` (User, Connection, Question, etc.)
- [x] Create API client: `src/api/client.ts` (Axios with auth interceptor)
- [x] Create Auth Context: `src/context/AuthContext.tsx`

**Verification:**
- [x] `npm run dev` starts app on localhost:5173
- [x] No TypeScript errors

---
#### Day 9: Login Page

**Tasks:**
- [x] Create `src/components/auth/LoginPage.tsx`:
  - "Sign in with Google" button
  - Constructs Cognito Hosted UI URL with Google provider
  - Redirects to Google OAuth
- [x] Create `src/pages/auth/CallbackPage.tsx`:
  - Handles OAuth callback with authorization code
  - Exchanges code for tokens via Cognito token endpoint
  - Stores tokens in localStorage
  - Calls `/auth/me` to get user profile
  - Redirects to dashboard
- [x] Create `src/App.tsx`:
  - React Router setup
  - Protected routes (require authentication)
  - Public routes: /login, /auth/callback

**Verification:**
- [x] Can click "Sign in with Google"
- [x] Redirects to Google consent screen
- [x] After approval, redirects back to app
- [x] Check browser console: tokens stored
- [x] Check browser network tab: `/auth/me` called successfully

**⚠️ MAJOR Trouble Spot:** OAuth callback is tricky. Common issues:
- Redirect URI mismatch → Check exact URL in Google Console matches
- CORS errors → Check API Gateway CORS settings
- Token exchange fails → Check Cognito domain is correct
- Budget 3-4 hours for debugging

**Checkpoint:** Can successfully login with Google and see user data in console.

---

#### Day 10: Dashboard Skeleton

**Tasks:**
- [x] Create `src/pages/DashboardPage.tsx`:
  - Shows user name and email
  - "Logout" button
  - Placeholder for questions/connections
- [x] Test full auth flow:
  - Login → Redirected to dashboard
  - Logout → Redirected to login
  - Try to access dashboard without login → Redirected to login

**Verification:**
- [x] Full authentication flow works end-to-end
- [x] User profile displays correctly
- [x] Can logout and login again

**⚠️ Checkpoint:** Authentication is 100% working before moving on. This is your foundation.

---

### **PHASE 3: Questions System** (Days 11-12) 🟢

#### Day 11: Hardcode 12 Questions

**Tasks:**
- [x] Create `shared/questions_data.py`:
```python
  QUESTIONS = [
      {"id": "q001", "text": "If you could...", "category": "life"},
      {"id": "q002", "text": "What's your...", "category": "random"},
      {"id": "q001", "text": "If you could...", "category": "deep"},
      {"id": "q002", "text": "What's your...", "category": "experiences"},
      # ... 166 more
  ]
```
- [x] Create seed script: `lambda_functions/questions/seed_data.py`
  - Reads from questions_data.py
  - Writes to DynamoDB with proper keys:
    - PK: `QUESTION#q001`
    - SK: `METADATA`
    - GSI1PK: `CATEGORY#life`
    - GSI1SK: `QUESTION#001`
- [x] Run seed script manually (one-time):
```bash
  python lambda_functions/questions/seed_data.py
```

**Verification:**
- [x] Check DynamoDB: 12 items with PK starting with `QUESTION#` and 1 item for user (totaling 13 items)
- [x] Spot check: Query by category using GSI `questions/test_gsi_query.py` file. 

---

#### Day 12: Random Question API

**Tasks:**
- [x] Create Lambda: `lambda_functions/questions/get_random.py`
  - Input: `category` (light/deep/flirty/creative)
  - Query DynamoDB using GSI: `CATEGORY#{category}`
  - Pick random question from results
  - Return question
- [x] Add route in API stack: `GET /questions/random?category=life`
- [x] Deploy
- [x] Create frontend: `src/pages/QuestionsPage.tsx`:
  - 4 category buttons
  - Click button → API call → Display random question
  - "Get Another" button (fetches new random)

**Verification:**
- [x] Click "life" → See random life question
- [x] Click "Get Another" → See different "life" question
- [x] All 4 categories work (life, random, deep, experiences)

**Checkpoint:** Can browse questions by category.

---

### **PHASE 4: Connections** (Days 13-15) 🟡

#### Day 13: Create Connection

**Tasks:**
- [x] Create Lambda: `lambda_functions/connections/create.py`
  - Input: `name` (e.g., "Sarah from Hinge")
  - Get user ID from JWT
  - Check if user is free tier:
    - Query DynamoDB: count connections for this user
    - If subscription_status='free' AND count >= 1 → Return 403 error
  - Generate connection_id (UUID)
  - Write to DynamoDB:
    - PK: `USER#{user_id}`
    - SK: `CONNECTION#{connection_id}`
    - name, created_at, etc.
  - Return connection object
- [x] Add route: `POST /connections` (requires auth)
- [x] Deploy
- [x] Create frontend: `src/components/connections/CreateConnectionModal.tsx`
  - Input field for name
  - "Create" button
  - Show error if paywall hit

**Verification:**
- [x] Create 1st connection: "Sarah" → Success
- [x] Try to create 2nd connection → Error: "Upgrade to Premium"

**⚠️ Trouble Spot:** Make sure free tier check happens BEFORE creating connection.

---

#### Day 14: List & Delete Connections

**Tasks:**
- [x] Create Lambda: `lambda_functions/connections/list.py`
  - Get user ID from JWT
  - Query DynamoDB: all items where PK=`USER#{user_id}` AND SK starts with `CONNECTION#`
  - Return list of connections
- [x] Create Lambda: `lambda_functions/connections/delete.py`
  - Input: connection_id
  - Verify connection belongs to user
  - Delete from DynamoDB
  - Also delete all usage records for this connection
- [x] Add routes:
  - `GET /connections`
  - `DELETE /connections/{id}`
- [x] Deploy
- [x] Create frontend: `src/pages/ConnectionsPage.tsx`
  - List all connections
  - "Add Connection" button
  - Delete button per connection

**Verification:**
- [x] Can see list of connections
- [x] Can delete a connection
- [x] After deleting, can create new connection (if was at limit)

---

#### Day 15: Connection Detail Page

**Tasks:**
- [x] Create `src/pages/ConnectionDetailPage.tsx`
  - Shows connection name
  - Placeholder: "Questions used with Sarah: 0"
  - Will add actual usage in next phase

**Verification:**
- [x] Click on connection → See detail page
- [x] Can navigate back to list (with the use of NavBar)

**Checkpoint:** Connection management fully working.

---

### **PHASE 5: Question Usage & Notes** (Days 16-18) 🟢

#### Day 16: Mark Question as Used

**Tasks:**
- [x] Create Lambda: `lambda_functions/usage/create.py`
  - Input: `connection_id`, `question_id`, `their_answer`, `my_answer`
  - Get user ID from JWT
  - Write to DynamoDB:
    - PK: `USER#{user_id}`
    - SK: `USAGE#{connection_id}#{question_id}`
    - GSI1PK: `CONNECTION#{connection_id}`
    - GSI1SK: `USAGE#{timestamp}`
  - Return usage object
- [x] Add route: `POST /connections/{id}/usage`
- [x] Deploy
- [x] Update QuestionsPage:
  - After showing random question, add "Use This Question" button
  - Opens modal: Select connection + 2 text areas (their answer, my answer)
  - Submit → Create usage record
  - Success message

**Verification:**
- [x] Get random question
- [x] Click "Use This Question"
- [x] Select "Sarah"
- [x] Enter both answers
- [x] Submit → Success

---

#### Day 17: View Usage History

**Tasks:**
- [x] Create Lambda: `lambda_functions/usage/list.py`
  - Input: connection_id
  - Query DynamoDB using GSI: `GSI1PK=CONNECTION#{connection_id}`
  - Return list of usage records with question text
- [x] Add route: `GET /connections/{id}/usage`
- [x] Deploy
- [x] Update ConnectionDetailPage:
  - Fetch usage history
  - Display list of questions used
  - Show their answer and your answer
  - Show date asked

**Verification:**
- [x] Go to Sarah's detail page
- [x] See list of questions you've used with her
- [x] See both answers for each

---

#### Day 18: Edit/Delete Usage

**Tasks:**
- [x] Create Lambda: `lambda_functions/usage/update.py`
  - Input: connection_id, question_id, new answers
  - Update DynamoDB item
- [x] Create Lambda: `lambda_functions/usage/delete.py`
  - Delete usage record
- [x] Add routes:
  - `PUT /connections/{id}/usage/{question_id}`
  - `DELETE /connections/{id}/usage/{question_id}`
- [x] Deploy
- [x] Update frontend: Add edit/delete buttons

**Verification:**
- [x] Can edit answers
- [x] Can delete usage record
- [x] Can re-use same question after deleting

**Checkpoint:** Full note-taking workflow works end-to-end.

---

#### Day 18.5: Polish & Quality of Life Improvements ✅

**Tasks Completed:**
- [x] **Navigation Bar**: Added navbar component for consistent navigation across pages
  - Links to Connections, Questions, Profile
  - Displays current page
  - Logout button
- [x] **Prevent Duplicate Questions**: Modified `get_random.py` to filter out already-used questions
  - Backend accepts `connection_id` query parameter
  - Queries usage history to exclude used questions
  - Returns error when all questions in category exhausted
- [x] **Category Badges in History**: Display question categories in conversation history
  - Modified `create.py` to store category with usage records
  - Modified `list.py` to return category in usage list
  - Frontend displays colored category badges (🌱 Life, 🎲 Random, 🤔 Deep, ✨ Experiences)
- [x] **Better Error Handling**: Show user-friendly message when all questions used
  - Yellow alert box displays: "You've used all questions in the 'X' category!"
- [x] **UI Polish**: Improved indentation and spacing in conversation history

**Files Modified:**
- Backend: `get_random.py`, `create.py`, `list.py`
- Frontend: `ConnectionDetailPage.tsx`, `App.tsx` (navbar)

**Verification:**
- [x] Cannot use same question twice with one connection
- [x] Can reuse same question with different connections
- [x] Category badges visible in conversation history
- [x] Clear error message when category exhausted
- [x] Navbar works on all pages

---

### **PHASE 6: Stripe Billing** (Days 19-21) 🔴

#### Day 19: Stripe Setup

**Tasks:**
- [ ] Create Stripe account: https://stripe.com/
- [ ] Stay in TEST mode
- [ ] Create product: "FlirtDeck Premium"
  - Price: $2.99/month
  - Recurring
  - Copy Price ID (e.g., `price_xxxxx`)
- [ ] Get API keys:
  - Publishable key (starts with `pk_test_`)
  - Secret key (starts with `sk_test_`)
- [ ] Store in AWS Secrets Manager:
```bash
  aws secretsmanager create-secret \
    --name flirtdeck/stripe \
    --secret-string '{"secret_key":"sk_test_xxxxx","price_id":"price_xxxxx"}' \
    --region us-west-2
```
- [ ] Grant Lambda permission to read secret

**Verification:**
- [ ] Stripe product created
- [ ] Secret stored in AWS
- [ ] Lambda can read secret (test with boto3)

**⚠️ Trouble Spot:** Don't commit Stripe keys to Git!

---

#### Day 20: Checkout Flow

**Tasks:**
- [ ] Create Lambda: `lambda_functions/billing/create_checkout.py`
  - Get user ID and email from JWT
  - Get Stripe keys from Secrets Manager
  - Create Stripe Customer (if doesn't exist)
  - Create Checkout Session:
    - Price ID from secret
    - Success URL: `{frontend_url}/billing/success`
    - Cancel URL: `{frontend_url}/billing/cancel`
    - Customer email pre-filled
    - Metadata: user_id
  - Return checkout session URL
- [ ] Add route: `POST /billing/create-checkout`
- [ ] Deploy
- [ ] Create frontend: `src/pages/UpgradePage.tsx`
  - Shows benefits of premium
  - "Upgrade for $2.99/month" button
  - Calls API → Redirects to Stripe Checkout
- [ ] Create success/cancel pages

**Verification:**
- [ ] Click "Upgrade" → Redirected to Stripe
- [ ] Use test card: 4242 4242 4242 4242
- [ ] Complete payment → Redirected to success page

**⚠️ Note:** Subscription not yet activated (need webhook).

---

#### Day 21: Webhook Handler

**Tasks:**
- [ ] Create Lambda: `lambda_functions/billing/webhook.py`
  - Verify Stripe signature
  - Handle events:
    - `checkout.session.completed` → Update user to premium
    - `customer.subscription.deleted` → Downgrade to free
  - Update DynamoDB: subscription_status, stripe_customer_id, stripe_subscription_id
- [ ] Add route: `POST /billing/webhook` (no auth, uses Stripe signature)
- [ ] Deploy
- [ ] Get webhook endpoint URL
- [ ] Configure in Stripe Dashboard:
  - Developers → Webhooks → Add endpoint
  - URL: `https://your-api-url/prod/billing/webhook`
  - Events: `checkout.session.completed`, `customer.subscription.deleted`
  - Copy webhook signing secret
- [ ] Add signing secret to Secrets Manager
- [ ] For local testing: Install Stripe CLI
```bash
  stripe listen --forward-to http://localhost:3000/billing/webhook
```

**Verification:**
- [ ] Complete Stripe checkout
- [ ] Webhook fires
- [ ] Check DynamoDB: user subscription_status = 'premium'
- [ ] Refresh app → Can now create unlimited connections
- [ ] Cancel subscription in Stripe → Webhook fires → Status = 'free'

**⚠️ MAJOR Trouble Spot:** Webhooks are notoriously difficult. Common issues:
- Signature verification fails → Check signing secret is correct
- Webhook not firing → Check Stripe dashboard logs
- Budget 3-4 hours for debugging

**Checkpoint:** Full payment flow works end-to-end. MVP is functionally complete!

---

### **PHASE 7: Frontend Hosting** (Day 22) 🟢

#### Day 22: Deploy Frontend to S3 + CloudFront

**Tasks:**
- [ ] Create `stacks/frontend_stack.py`:
  - S3 bucket for static hosting
  - CloudFront distribution
  - OAI (Origin Access Identity)
  - Default root object: index.html
  - Error pages: 404 → /index.html (for SPA routing)
- [ ] Deploy stack:
```bash
  cdk deploy FrontendStack
```
- [ ] Copy CloudFront URL from outputs
- [ ] Update `.env.local` → `.env.production`:
```
  VITE_REDIRECT_URI=https://YOUR-CLOUDFRONT-URL/auth/callback
```
- [ ] Build frontend:
```bash
  npm run build
```
- [ ] Upload to S3:
```bash
  aws s3 sync dist/ s3://YOUR-BUCKET-NAME/ --delete
```
- [ ] Invalidate CloudFront cache:
```bash
  aws cloudfront create-invalidation --distribution-id YOUR-DIST-ID --paths "/*"
```
- [ ] Update Google OAuth:
  - Add CloudFront URL to authorized redirect URIs
- [ ] Update Cognito User Pool Client:
  - Add CloudFront callback/logout URLs

**Verification:**
- [ ] Visit CloudFront URL → App loads
- [ ] Can login with Google
- [ ] Full flow works in production

**Checkpoint:** App is live and accessible!

---

### **PHASE 8: CI/CD Pipeline** (Days 23-24) 🔴

#### Day 23: Backend CI/CD

**Tasks:**
- [ ] Create `stacks/cicd_stack.py`:
  - CodePipeline
  - Source: GitHub connection
  - Build: CodeBuild project
    - Install dependencies
    - Run tests (if any)
    - CDK synth
    - CDK deploy
  - Trigger on push to `main` branch
- [ ] Create `buildspec.yml` in backend/infrastructure:
```yaml
  version: 0.2
  phases:
    install:
      runtime-versions:
        python: 3.11
      commands:
        - npm install -g aws-cdk
        - pip install -r requirements.txt
    build:
      commands:
        - cdk synth
        - cdk deploy --all --require-approval never
```
- [ ] Deploy CICD stack
- [ ] Connect GitHub repo to CodePipeline
- [ ] Test: Push to main → Pipeline runs → Backend deploys

**Verification:**
- [ ] Push code change to GitHub
- [ ] CodePipeline triggers automatically
- [ ] Build succeeds
- [ ] Changes deployed to AWS

**⚠️ Trouble Spot:** GitHub connection requires OAuth approval in AWS Console.

---

#### Day 24: Frontend CI/CD

**Tasks:**
- [ ] Create `.github/workflows/frontend-deploy.yml`:
```yaml
  name: Deploy Frontend
  on:
    push:
      branches: [main]
      paths: ['frontend/**']
  jobs:
    deploy:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - uses: actions/setup-node@v3
        - run: cd frontend && npm install
        - run: cd frontend && npm run build
        - uses: aws-actions/configure-aws-credentials@v2
        - run: aws s3 sync frontend/dist/ s3://BUCKET/ --delete
        - run: aws cloudfront create-invalidation --distribution-id ID --paths "/*"
```
- [ ] Add GitHub secrets:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
- [ ] Test: Push frontend change → GitHub Action runs → Deployed to S3

**Verification:**
- [ ] Push frontend code change
- [ ] GitHub Action succeeds
- [ ] Visit CloudFront URL → Changes live

**Checkpoint:** Full CI/CD working. Any push to main auto-deploys!

---

### **PHASE 9: Monitoring & Observability** (Days 25-26) 🟡

#### Day 25: CloudWatch Dashboard

**Tasks:**
- [ ] Create `stacks/monitoring_stack.py`:
  - CloudWatch Dashboard: "FlirtDeck Metrics"
  - Widgets:
    - API Gateway: Request count, 4XX errors, 5XX errors, latency
    - Lambda: Invocations, errors, duration, throttles
    - DynamoDB: Read/write capacity, throttled requests
    - Custom metrics (next task)
- [ ] Deploy monitoring stack

**Verification:**
- [ ] Open CloudWatch → Dashboards → FlirtDeck Metrics
- [ ] See real-time data from your API calls

---

#### Day 26: Custom Metrics & Alarms

**Tasks:**
- [ ] Add custom metrics to Lambdas:
  - User signups (CloudWatch PutMetric)
  - Connections created
  - Questions
  - Questions used
  - Upgrade conversions
  - Free tier limit hits
- [ ] Update Lambda functions to emit metrics:
```python
  import boto3
  cloudwatch = boto3.client('cloudwatch')
  
  cloudwatch.put_metric_data(
      Namespace='FlirtDeck',
      MetricData=[{
          'MetricName': 'UserSignup',
          'Value': 1,
          'Unit': 'Count'
      }]
  )
```
- [ ] Create CloudWatch Alarms:
  - API Gateway 5XX errors > 5 in 5 minutes → SNS email
  - Lambda errors > 10 in 5 minutes → SNS email
  - No signups in 24 hours → SNS email (optional)
- [ ] Create SNS topic and subscribe your email
- [ ] Update monitoring stack with alarms
- [ ] Deploy

**Verification:**
- [ ] Trigger error intentionally → Receive alarm email
- [ ] Dashboard shows custom metrics
- [ ] Use app → See metrics update in real-time

**Checkpoint:** Full production monitoring in place!

---

### **PHASE 10: Documentation & Polish** (Days 27-28) 🟢

#### Day 27: Architecture Diagram

**Tasks:**
- [ ] Create professional architecture diagram:
  - Use draw.io, Lucidchart, or CloudCraft
  - Show all AWS services and connections
  - Include CI/CD flow
  - Include monitoring
- [ ] Save as `docs/architecture.png`
- [ ] Add to README

**Verification:**
- [ ] Diagram clearly shows entire system
- [ ] All 11 AWS services labeled
- [ ] Flow is easy to understand

---

#### Day 28: README & Documentation

**Tasks:**
- [ ] Write comprehensive README.md:
  
  **Sections:**
  1. **Project Overview**
     - What it does
     - Why I built it
     - Demo link (CloudFront URL)
  
  2. **Architecture**
     - Embed architecture diagram
     - List all AWS services used
     - Brief description of each
  
  3. **Tech Stack**
     - Backend: Python, CDK, Lambda
     - Frontend: React, TypeScript, Vite
     - Database: DynamoDB single-table design
     - CI/CD: CodePipeline + GitHub Actions
  
  4. **Key Features**
     - Google OAuth authentication
     - Multi-tenant data isolation
     - Stripe subscription billing
     - Real-time monitoring
     - Automated deployments
  
  5. **Design Decisions**
     - Why DynamoDB over RDS (cost, scalability)
     - Why single-table design (fewer API calls)
     - Why serverless (cost, auto-scaling)
     - Why Python CDK (developer experience)
  
  6. **Security**
     - Cognito for authentication
     - IAM least-privilege roles
     - Secrets Manager for credentials
     - API Gateway authorization
     - HTTPS everywhere
  
  7. **Cost Analysis**
     - Monthly breakdown
     - Optimization strategies
     - Expected costs at scale
  
  8. **Monitoring & Observability**
     - CloudWatch dashboard
     - Custom metrics tracked
     - Alerting strategy
  
  9. **CI/CD Pipeline**
     - Automated testing (if any)
     - Deployment process
     - Rollback strategy
  
  10. **Local Development Setup**
      - Prerequisites
      - Installation steps
      - Environment variables needed
  
  11. **Deployment Instructions**
      - AWS account setup
      - CDK bootstrap
      - Deploy commands
  
  12. **What I'd Do Differently at Scale**
      - Add caching (CloudFront, Redis)
      - Implement rate limiting
      - Add API versioning
      - Set up multi-region failover
      - Add comprehensive testing suite
      - Implement feature flags
  
  13. **Lessons Learned**
      - Challenges faced
      - How you solved them
      - What you'd do differently next time
  
  14. **Future Enhancements** (Phase 2)
      - AI-powered question suggestions (Bedrock)
      - Email notifications (SES)
      - Custom questions
      - Mobile app
      - Analytics dashboard
  
  15. **Contact**
      - LinkedIn
      - GitHub
      - Portfolio website

- [ ] Add code comments to complex sections
- [ ] Create `docs/cost-analysis.md` with detailed breakdown
- [ ] Create `CHANGELOG.md` documenting versions

**Verification:**
- [ ] README is professional and comprehensive
- [ ] Someone could deploy this following your instructions
- [ ] Architecture is well-explained

---

#### Day 28 (continued): Final Testing

**Tasks:**
- [ ] **End-to-End Test:**
  - [ ] New user signs up with Google
  - [ ] Browses questions by category
  - [ ] Creates connection "Sarah"
  - [ ] Uses question and logs answers
  - [ ] Tries to create 2nd connection → Paywall
  - [ ] Upgrades to premium
  - [ ] Creates unlimited connections
  - [ ] Views usage history
  - [ ] Edits/deletes usage
  - [ ] Logs out and back in
  
- [ ] **Edge Cases:**
  - [ ] Try to access protected routes without auth
  - [ ] Try to access another user's connections
  - [ ] Cancel subscription → Can't create new connections
  - [ ] Delete connection with usage history
  
- [ ] **Browser Testing:**
  - [ ] Chrome
  - [ ] Firefox
  - [ ] Safari
  - [ ] Mobile (responsive design)

- [ ] **Performance Check:**
  - [ ] Page load < 3 seconds
  - [ ] API responses < 500ms
  - [ ] No console errors

**Verification:**
- [ ] All workflows work perfectly
- [ ] No bugs found
- [ ] App feels polished

---

### **PHASE 11: Demo & Portfolio Integration** (Day 29) 🟢

#### Day 29: Create Demo Materials

**Tasks:**
- [ ] **Record Demo Video** (3-5 minutes):
  - Introduction: What is FlirtDeck
  - Login with Google
  - Browse questions
  - Create connection
  - Use question and log answers
  - Hit paywall
  - Upgrade flow
  - Show premium features
  - Quick architecture overview
  - Highlight AWS services used
  
- [ ] Upload to YouTube (unlisted)
- [ ] Add video link to README

- [ ] **Take Screenshots:**
  - Login page
  - Questions page
  - Connections list
  - Usage history
  - Upgrade page
  - CloudWatch dashboard
  - Architecture diagram
  
- [ ] Add to `docs/screenshots/` folder

- [ ] **Write Blog Post** (Optional but impressive):
  - "Building a Multi-Tenant SaaS on AWS"
  - Technical deep-dive
  - Challenges and solutions
  - Publish on Medium/Dev.to
  - Add link to README

**Verification:**
- [ ] Demo video clearly shows all features
- [ ] Screenshots look professional
- [ ] All materials added to repo

---

#### Day 29 (continued): Portfolio Integration

**Tasks:**
- [ ] Add to your portfolio website
- [ ] Update LinkedIn:
  - Add project to Projects section
  - Post about completion with demo video
  - Tag relevant AWS services
- [ ] Update resume:
  - Add FlirtDeck under Projects
  - Mention: "Multi-tenant SaaS built on AWS with CI/CD, monitoring, and Stripe integration"
  - List AWS services used
- [ ] Share on Twitter/X (optional):
  - Brief thread about building it
  - Include demo and architecture diagram
  - Use hashtags: #AWS #CloudComputing #DevOps

**Verification:**
- [ ] Project visible on portfolio
- [ ] LinkedIn updated
- [ ] Resume updated

---

### **PHASE 12: Interview Preparation** (Day 30) 🟢

#### Day 30: Prepare to Discuss

**Tasks:**
- [ ] **Create Interview Talking Points Document:**
  
  **Architecture Questions:**
  - Why serverless over containers?
  - Why DynamoDB over RDS?
  - How does single-table design work?
  - How do you handle multi-tenancy?
  - What's your disaster recovery strategy?
  
  **Cost Questions:**
  - Monthly cost breakdown
  - How would costs scale to 10K users?
  - What optimizations did you implement?
  
  **Security Questions:**
  - How is user data isolated?
  - How do you secure API endpoints?
  - How are secrets managed?
  - What's your IAM strategy?
  
  **DevOps Questions:**
  - Walk through your CI/CD pipeline
  - How do you handle rollbacks?
  - What monitoring is in place?
  - How do you debug production issues?
  
  **Scaling Questions:**
  - What would break first at scale?
  - How would you handle 1M users?
  - What caching strategy would you add?
  - How would you implement multi-region?
  
  **Lessons Learned:**
  - Biggest challenge and how you solved it
  - What you'd do differently
  - What you learned about AWS

- [ ] Practice explaining architecture in 2 minutes
- [ ] Practice explaining one technical challenge in detail
- [ ] Review AWS service documentation for services used

**Verification:**
- [ ] Can confidently explain every part of system
- [ ] Can discuss trade-offs intelligently
- [ ] Ready to demo live in interviews

---

## 🎯 Success Criteria - "Definition of Done"

### Functional Requirements:
- ✅ Users can login with Google OAuth
- ✅ Users can browse questions by category
- ✅ Users can create connections (names only)
- ✅ Free users limited to 1 connection
- ✅ Users can mark questions as used and log answers
- ✅ Users can view usage history per connection
- ✅ Users can upgrade via Stripe ($2.99/month)
- ✅ Premium users have unlimited connections
- ✅ Subscription cancellation downgrades account

### Technical Requirements:
- ✅ All infrastructure defined in CDK
- ✅ DynamoDB single-table design implemented
- ✅ API Gateway with Cognito authorization
- ✅ Secrets managed in Secrets Manager
- ✅ CI/CD pipeline auto-deploys on push
- ✅ CloudWatch dashboard with custom metrics
- ✅ CloudWatch alarms send email alerts
- ✅ Frontend hosted on S3 + CloudFront
- ✅ HTTPS everywhere
- ✅ IAM least-privilege roles

### Portfolio Requirements:
- ✅ Professional README with architecture diagram
- ✅ Demo video recorded and linked
- ✅ Clean, commented code
- ✅ Cost analysis documented
- ✅ Design decisions explained
- ✅ Working production deployment
- ✅ Added to portfolio website
- ✅ LinkedIn/resume updated

---

## 🚨 Common Trouble Spots & Solutions

### Issue: Cognito OAuth Not Working
**Symptoms:** Redirect loops, "Invalid redirect URI" errors

**Solutions:**
- Verify redirect URIs match EXACTLY in Google Console and Cognito (no trailing slashes)
- Check Cognito domain is correct format
- Ensure OAuth consent screen is published
- Clear browser cookies and try again
- Check browser console for CORS errors

**Debug Steps:**
1. Check Google Console → Credentials → Authorized redirect URIs
2. Check Cognito → App clients → Callback URLs
3. Verify Cognito domain in CDK outputs matches what you're using
4. Test with Incognito window

---

### Issue: Stripe Webhook Not Firing
**Symptoms:** Payment succeeds but user not upgraded

**Solutions:**
- Check Stripe Dashboard → Webhooks → View logs
- Verify webhook URL is correct (include `/prod/` if using API Gateway stages)
- Verify signing secret matches in Secrets Manager
- Check Lambda CloudWatch logs for errors
- Use Stripe CLI for local testing first

**Debug Steps:**
1. Stripe Dashboard → Developers → Webhooks → Click your endpoint → View attempts
2. Check HTTP status code (should be 200)
3. Check Lambda CloudWatch logs for webhook Lambda
4. Verify signature verification code is correct

---

### Issue: DynamoDB Query Returns Nothing
**Symptoms:** API returns empty array when data exists

**Solutions:**
- Verify you're querying with correct PK/SK format
- Check if you need to use GSI for your query
- Verify data was actually written (check DynamoDB console)
- Check for typos in key names (case-sensitive)
- Use `scan` temporarily to see all data (expensive, debug only)

**Debug Steps:**
1. Go to DynamoDB console → Tables → flirtdeck-table → Explore items
2. Verify data exists with expected PK/SK format
3. Check Lambda CloudWatch logs for actual query parameters
4. Add debug logging: `print(f"Querying with PK={pk}, SK={sk}")`

---

### Issue: CORS Errors in Browser
**Symptoms:** API calls fail with "CORS policy" error

**Solutions:**
- Add correct origins to API Gateway CORS config
- Include `Access-Control-Allow-Credentials: true` for authenticated requests
- Ensure Lambda returns CORS headers in response
- Check OPTIONS preflight is handled
- Verify API Gateway has CORS enabled on route

**Debug Steps:**
1. Check browser Network tab → Failed request → Response headers
2. Verify `Access-Control-Allow-Origin` header present
3. Check API Gateway → Resources → Enable CORS
4. Redeploy API Gateway after CORS changes

---

### Issue: CDK Deploy Fails
**Symptoms:** `cdk deploy` errors out

**Common Causes:**
- AWS credentials not configured: Run `aws configure`
- CDK not bootstrapped: Run `cdk bootstrap aws://ACCOUNT/REGION`
- IAM permissions insufficient: Check your IAM user has admin/PowerUser
- Resource name conflicts: Change stack names or resource IDs
- Python dependencies missing: Run `pip install -r requirements.txt`

**Debug Steps:**
1. Run `aws sts get-caller-identity` (verify AWS credentials work)
2. Run `cdk synth` (check for synthesis errors)
3. Check error message for specific resource causing issue
4. Check CloudFormation console for stack events

---

### Issue: High AWS Costs
**Symptoms:** Bill higher than expected

**Common Causes:**
- NAT Gateway left running ($32/month) - Don't use NAT for this project
- ALB left running ($16/month) - We use API Gateway instead
- CloudWatch Logs not configured with retention - Set 7-day retention
- DynamoDB in provisioned mode - Use on-demand

**Prevention:**
- Set up billing alerts ($10, $20, $50 thresholds)
- Use Cost Explorer to identify culprits
- Tag all resources: `Project=FlirtDeck`
- Delete unused stacks: `cdk destroy`
- Review "Estimated monthly costs" in AWS Console

---

### Issue: Frontend Not Loading After Deploy
**Symptoms:** CloudFront shows blank page or 404

**Solutions:**
- Check S3 bucket has files: `aws s3 ls s3://BUCKET-NAME/`
- Verify CloudFront default root object is `index.html`
- Invalidate CloudFront cache: `aws cloudfront create-invalidation...`
- Check CloudFront error pages configuration (404 → /index.html for SPA)
- Verify S3 bucket policy allows CloudFront OAI access

**Debug Steps:**
1. Visit S3 bucket URL directly (will fail, but check browser console)
2. Check CloudFront distribution settings → Origins
3. Check CloudFront error pages configuration
4. Invalidate entire cache: `/*`
5. Wait 5-10 minutes for invalidation to complete

---

## 📊 Cost Breakdown (Monthly)

### MVP Cost (Development/Demo):
- **DynamoDB:** $0 (on-demand, free tier covers light usage)
- **Lambda:** $0 (1M requests + 400K GB-seconds free)
- **API Gateway:** $0 (first 12 months free, then $3.50/1M requests)
- **Cognito:** $0 (free tier: 50K MAUs)
- **S3:** ~$0.50 (storage)
- **CloudFront:** ~$1-2 (data transfer)
- **Secrets Manager:** $0.40/secret × 1 = $0.40
- **CloudWatch:** $0-2 (5GB logs free)
- **CodePipeline:** $1/pipeline (first 30 days free)
- **CodeBuild:** $0 (100 build minutes free)

**Total: $3-8/month**

### At Scale (1,000 active users):
- **DynamoDB:** ~$5 (on-demand)
- **Lambda:** ~$2 (beyond free tier)
- **API Gateway:** ~$5
- **Cognito:** $0 (still in free tier)
- **S3 + CloudFront:** ~$5
- **Secrets Manager:** $0.40
- **CloudWatch:** ~$5
- **CodePipeline:** $1

**Total: ~$25-30/month**

### Cost Optimization Tips:
- Use CloudFront caching aggressively
- Set CloudWatch log retention to 7 days
- Use DynamoDB on-demand (not provisioned)
- Don't use NAT Gateway
- Delete unused stacks during development
- Use S3 lifecycle policies for old logs

---

## 🎓 Interview Preparation Guide

### Question: "Walk me through your FlirtDeck architecture"

**Your Answer (2-minute version):**

"FlirtDeck is a multi-tenant SaaS application built entirely on AWS serverless technologies. 

The frontend is a React TypeScript SPA hosted on S3 with CloudFront for global CDN distribution. Users authenticate via Cognito with Google OAuth integration.

The backend uses API Gateway as the entry point, which validates JWT tokens from Cognito before routing to Lambda functions. I have separate Lambda functions for auth, questions, connections, and billing - following single-responsibility principle.

All data lives in a single DynamoDB table using a multi-tenant single-table design pattern. I use composite keys with PK/SK patterns like USER#123 / CONNECTION#456 for efficient queries and strong tenant isolation.

For billing, I integrated Stripe for subscription management. When users hit the free tier limit of 1 connection, they're prompted to upgrade. Stripe webhooks notify my Lambda function when subscriptions change, updating user status in DynamoDB.

The entire infrastructure is defined as code using AWS CDK in Python, which generates CloudFormation templates. I have a CI/CD pipeline with CodePipeline that automatically deploys backend changes when I push to GitHub, and GitHub Actions handles frontend deployments.

For observability, I built a CloudWatch dashboard tracking custom metrics like signups, upgrades, and question usage, with alarms that email me if error rates spike.

The whole system costs about $5 per month to run and can scale to thousands of users without code changes thanks to serverless auto-scaling."

---

### Question: "What was your biggest technical challenge?"

**Your Answer:**

"The biggest challenge was implementing the Stripe webhook handler correctly. 

The issue was that Stripe sends webhook events asynchronously, and I needed to verify the signature, handle different event types, and update DynamoDB atomically - all while ensuring idempotency in case Stripe retries the webhook.

Initially, I was getting signature verification failures. I debugged by checking the raw request body, verified my signing secret was correct, and realized I needed to use the exact raw body, not the parsed JSON.

I also had to handle race conditions where a user might try to create a second connection while the webhook was still processing their upgrade. I solved this by having the connection creation Lambda always fetch the latest subscription status from DynamoDB rather than caching it.

To test webhooks locally, I used the Stripe CLI to forward events to my local Lambda, which made debugging much faster than deploying to AWS each time.

This taught me a lot about webhook best practices: signature verification, idempotency keys, and defensive programming for async events."

---

### Question: "How would you scale this to 100K users?"

**Your Answer:**

"Great question. At 100K users, several things would need to change:

**Caching:** I'd add CloudFront caching for the questions API since that data rarely changes. I'd also implement Redis/ElastiCache for user session data and frequently accessed connection lists.

**Database:** DynamoDB would handle 100K users fine due to its horizontal scaling, but I'd monitor for hot partitions and potentially add more GSIs for different access patterns. I'd also implement DynamoDB DAX for read-heavy queries.

**API:** I'd implement rate limiting at the API Gateway level to prevent abuse, and add API keys for tracking usage per user tier.

**Monitoring:** I'd add X-Ray for distributed tracing to identify bottlenecks across services. I'd also implement more granular custom metrics and anomaly detection.

**Frontend:** I'd add lazy loading for components, implement service workers for offline capability, and add React Query for better client-side caching.

**Regional:** For global users, I'd deploy API Gateway and Lambda functions in multiple regions, with DynamoDB global tables for low-latency reads worldwide.

**Cost:** At this scale, I'd negotiate volume pricing with Stripe and potentially move some compute to Fargate for long-running processes to avoid Lambda cost creep.

The beauty of serverless is that most of this scales automatically - I'd mainly focus on caching and monitoring optimizations."

---

### Question: "Why DynamoDB instead of RDS?"

**Your Answer:**

"I chose DynamoDB for several reasons specific to this application:

**Cost:** For a portfolio project with unpredictable traffic, DynamoDB's on-demand billing meant I only pay for actual usage. RDS would cost $15-20/month minimum even idle.

**Scaling:** DynamoDB automatically scales with zero downtime. With RDS, I'd need to provision capacity upfront and manage scaling events.

**Serverless fit:** DynamoDB integrates perfectly with Lambda - no connection pooling issues, no cold start delays from establishing DB connections.

**Access patterns:** My queries are simple key-value lookups and single-table queries, which DynamoDB excels at. I don't need complex JOINs or transactions across multiple entities.

**Multi-tenancy:** DynamoDB's partition key design makes tenant isolation natural - each user's data is inherently isolated by the USER#{id} partition key.

That said, if this were a complex application with lots of relational queries, reporting needs, or required ACID transactions across multiple entities, I'd reconsider RDS. The single-table design pattern requires more upfront planning, and you lose the flexibility of ad-hoc SQL queries.

But for this use case - simple CRUD operations with predictable access patterns - DynamoDB was the right choice."

---

## ✅ Final Checklist Before Calling It Done

### Code Quality:
- [ ] No console.log or print statements in production code
- [ ] All sensitive data in Secrets Manager (no hardcoded keys)
- [ ] Error handling in all Lambda functions
- [ ] Input validation on all API endpoints
- [ ] TypeScript strict mode enabled
- [ ] No TypeScript `any` types (or minimal with comments)
- [ ] Python type hints used consistently
- [ ] Code is DRY (shared utilities extracted)

### Security:
- [ ] IAM roles follow least-privilege
- [ ] API endpoints require authentication (except public ones)
- [ ] Cognito token validation working
- [ ] Stripe signature verification working
- [ ] CORS configured correctly (not `*` wildcard)
- [ ] Secrets not in Git history (`git log --all -- credentials.txt`)
- [ ] S3 bucket not publicly accessible (CloudFront only)
- [ ] HTTPS enforced everywhere

### Testing:
- [ ] Tested all user flows end-to-end
- [ ] Tested free tier limits
- [ ] Tested upgrade flow with Stripe test card
- [ ] Tested webhook with Stripe CLI
- [ ] Tested on multiple browsers
- [ ] Tested responsive design on mobile
- [ ] Tested error scenarios (network failures, invalid input)
- [ ] Tested logout/re-login

### Documentation:
- [ ] README is comprehensive and professional
- [ ] Architecture diagram included
- [ ] All AWS services listed and explained
- [ ] Setup instructions clear and complete
- [ ] Cost analysis documented
- [ ] Design decisions explained
- [ ] Demo video recorded and linked
- [ ] Code comments on complex logic

### Deployment:
- [ ] All infrastructure in CDK (no manual AWS console changes)
- [ ] CI/CD pipeline working
- [ ] CloudWatch dashboard visible and useful
- [ ] Alarms configured and tested
- [ ] Frontend accessible via CloudFront
- [ ] All environment variables documented
- [ ] Can deploy from scratch following README

### Portfolio:
- [ ] Added to portfolio website
- [ ] LinkedIn updated with project
- [ ] Resume includes project
- [ ] Demo video polished and professional
- [ ] Screenshots added to repo
- [ ] Can explain every design decision

---

## 🎉 You're Done! What's Next?

### Immediate (This Week):
1. **Start Applying** - You have a killer portfolio project now
2. **Share on LinkedIn** - Post about completion with demo video
3. **Practice Interview Answers** - Use the guide above
4. **Network** - Share project in AWS communities

### Short Term (Next Month):
1. **Get Feedback** - Ask for code reviews in AWS communities
2. **Blog Post** - Write about building it (great for SEO)
3. **Add to GitHub Profile README** - Pin the repo
4. **Record Architecture Deep-Dive** - 10-min technical video

### Long Term (Optional Phase 2):
1. **Add AI Features** - Integrate AWS Bedrock for question suggestions
2. **Email Notifications** - Add SES for welcome emails
3. **Analytics Dashboard** - Add admin panel with usage metrics
4. **Multi-Region** - Deploy to multiple AWS regions
5. **Mobile App** - React Native version
6. **Open Source** - Make it a template others can use

---

## 📚 Additional Resources

### AWS Documentation:
- [DynamoDB Single-Table Design](https://aws.amazon.com/blogs/compute/creating-a-single-table-design-with-amazon-dynamodb/)
- [Cognito OAuth Flows](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-app-integration.html)
- [API Gateway Best Practices](https://docs.aws.amazon.com/apigateway/latest/developerguide/best-practices.html)
- [Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)

### Learning:
- [AWS Skill Builder](https://skillbuilder.aws/) - Free courses
- [AWS Workshops](https://workshops.aws/) - Hands-on tutorials
- [AWS Architecture Blog](https://aws.amazon.com/blogs/architecture/)

### Communities:
- [r/aws](https://reddit.com/r/aws)
- [AWS Community Discord](https://discord.gg/aws)
- [AWS DevOps Pro Slack](https://awsdevopspro.slack.com)

---

## 🤝 Need Help?

If you get stuck during implementation:

1. **Check AWS CloudWatch Logs** - 80% of issues show up here
2. **Use CDK Diff** - `cdk diff` shows what will change before deploying
3. **AWS Forums** - Search for error messages
4. **Stack Overflow** - Tag questions with `aws-cdk`, `aws-lambda`, etc.
5. **GitHub Issues** - Check AWS CDK GitHub for known issues

**Remember:** Code slow = code fast. Test each phase thoroughly before moving on.

---

## 🎯 Your Mission

Build this. Ship it. Get hired.

This project demonstrates you can:
- Design cloud-native architectures
- Write production-quality code
- Implement security best practices
- Build CI/CD pipelines
- Monitor production systems
- Work with third-party APIs
- Think about costs and scaling
- Document and communicate effectively

**You've got this. Now go build it!** 🚀


