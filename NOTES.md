Continuation of Chat

FlirtDeck AWS project structure:

backend/
├── infrastructure/
│   └── infrastructure/
│       └── api_stack.py
└── lambda_functions/
    ├── shared/          ← Shared utilities HERE
    │   ├── responses.py
    │   ├── dynamodb.py
    │   └── questions_data.py
    ├── auth/
    │   └── get_me.py
    └── questions/
        └── get_random.py

Lambda packaging: CDK packages entire lambda_functions/ folder
Handler format: auth.get_me.handler or questions.get_random.handler
Imports in Lambda files: from shared.responses import ...

NEVER change api_stack.py Lambda packaging without asking first.