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



# Get your auth token from browser (after logging in):
# DevTools → Application → Local Storage → Copy the ID token

{"id": "life_001", "text": "If you could master any skill instantly, what would it be and why?", "category": "life"}%  



# Get your idToken from browser localStorage (same as before)

# Test creating first connection (should succeed)

curl -X POST \
  -H "Authorization: Bearer eyJraWQiOiJ0NlFyYkJBXC9BeDdMdDhlaTlmTlBiK21PMlFDN3FhMWVyejZ4cERZWGFQMD0iLCJhbGciOiJSUzI1NiJ9.eyJhdF9oYXNoIjoiSTNjWnZkR3NXcTZPbVYxZW1oNU5GZyIsInN1YiI6ImQ4ZDE3MzMwLTUwOTEtNzBmMi00YzE0LTMzZjhmNTE2NTE0MiIsImNvZ25pdG86Z3JvdXBzIjpbInVzLXdlc3QtMl9rY1o2WkpKdnlfR29vZ2xlIl0sImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLXdlc3QtMi5hbWF6b25hd3MuY29tXC91cy13ZXN0LTJfa2NaNlpKSnZ5IiwiY29nbml0bzp1c2VybmFtZSI6Ikdvb2dsZV8xMDAxMjAzNjIyOTQzMTkzMzk3ODIiLCJnaXZlbl9uYW1lIjoiS2VubmV0aCIsInBpY3R1cmUiOiJodHRwczpcL1wvbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbVwvYVwvQUNnOG9jSXJYS09Yc1g3cmQtakRFOURsMDVzLTVFc0dyRHI3X0dNbDk4Z3JyOFctaS1aQ1JFblM9czk2LWMiLCJvcmlnaW5fanRpIjoiMWQ5MDhjODYtYjNhMi00ZTY2LTk1ZWItODBlNTE2ODE1ZjE1IiwiYXVkIjoiMXB1ajlkbWVrajJvNzZidjgycDlzbmRwNWsiLCJpZGVudGl0aWVzIjpbeyJkYXRlQ3JlYXRlZCI6IjE3NjI4MTMxNzgwOTYiLCJ1c2VySWQiOiIxMDAxMjAzNjIyOTQzMTkzMzk3ODIiLCJwcm92aWRlck5hbWUiOiJHb29nbGUiLCJwcm92aWRlclR5cGUiOiJHb29nbGUiLCJpc3N1ZXIiOm51bGwsInByaW1hcnkiOiJ0cnVlIn1dLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTc2MjkyNDgxMCwiZXhwIjoxNzYyOTI4NDEwLCJpYXQiOjE3NjI5MjQ4MTAsImZhbWlseV9uYW1lIjoiQ2hhbmciLCJqdGkiOiJhODkzMTA5NS01ZGU4LTRiZjYtODUxMS1mMjY1NzUxODgyZDgiLCJlbWFpbCI6Imtlbm5ldGhwY2hhbmdAZ21haWwuY29tIn0.Phe7LWpVxTrTtMuaigXUM2mmv8vd0VeSO12V-iRqihXJrBdvNecvzQGjE0PT6JLg-yuolZfRplLvGoqmdeknssIXf7XZAp7FJUXlruW9lKLpINplpTfxvEjvLc1CW7ntyoAGQUHXCR8Ifot30gaYi9TuhRuRaYw5tafYJjMrJZCsaPXIDP_xda4XwLAvifWuu3S-ISF2HW0OrOigPjAzPc1vz6wTRDZS2kASHQa5DhQtzc_xsqJcyD0FYfFNqlWsEMdiIA_hHgXi327Xcsv0C3NqrmI5tkr0MljzZwElWrelBDudqdIS66-HxU8oNQDM4xpa-JJ13b9jy2y7vd23MA" \
  -H "Content-Type: application/json" \
  -d '{"name": "Sarah from Hinge"}' \
  "https://fdhf52udwe.execute-api.us-west-2.amazonaws.com/prod/connections"



curl -X POST \
  -H "Authorization: Bearer eyJraWQiOiJ0NlFyYkJBXC9BeDdMdDhlaTlmTlBiK21PMlFDN3FhMWVyejZ4cERZWGFQMD0iLCJhbGciOiJSUzI1NiJ9.eyJhdF9oYXNoIjoiSTNjWnZkR3NXcTZPbVYxZW1oNU5GZyIsInN1YiI6ImQ4ZDE3MzMwLTUwOTEtNzBmMi00YzE0LTMzZjhmNTE2NTE0MiIsImNvZ25pdG86Z3JvdXBzIjpbInVzLXdlc3QtMl9rY1o2WkpKdnlfR29vZ2xlIl0sImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLXdlc3QtMi5hbWF6b25hd3MuY29tXC91cy13ZXN0LTJfa2NaNlpKSnZ5IiwiY29nbml0bzp1c2VybmFtZSI6Ikdvb2dsZV8xMDAxMjAzNjIyOTQzMTkzMzk3ODIiLCJnaXZlbl9uYW1lIjoiS2VubmV0aCIsInBpY3R1cmUiOiJodHRwczpcL1wvbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbVwvYVwvQUNnOG9jSXJYS09Yc1g3cmQtakRFOURsMDVzLTVFc0dyRHI3X0dNbDk4Z3JyOFctaS1aQ1JFblM9czk2LWMiLCJvcmlnaW5fanRpIjoiMWQ5MDhjODYtYjNhMi00ZTY2LTk1ZWItODBlNTE2ODE1ZjE1IiwiYXVkIjoiMXB1ajlkbWVrajJvNzZidjgycDlzbmRwNWsiLCJpZGVudGl0aWVzIjpbeyJkYXRlQ3JlYXRlZCI6IjE3NjI4MTMxNzgwOTYiLCJ1c2VySWQiOiIxMDAxMjAzNjIyOTQzMTkzMzk3ODIiLCJwcm92aWRlck5hbWUiOiJHb29nbGUiLCJwcm92aWRlclR5cGUiOiJHb29nbGUiLCJpc3N1ZXIiOm51bGwsInByaW1hcnkiOiJ0cnVlIn1dLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTc2MjkyNDgxMCwiZXhwIjoxNzYyOTI4NDEwLCJpYXQiOjE3NjI5MjQ4MTAsImZhbWlseV9uYW1lIjoiQ2hhbmciLCJqdGkiOiJhODkzMTA5NS01ZGU4LTRiZjYtODUxMS1mMjY1NzUxODgyZDgiLCJlbWFpbCI6Imtlbm5ldGhwY2hhbmdAZ21haWwuY29tIn0.Phe7LWpVxTrTtMuaigXUM2mmv8vd0VeSO12V-iRqihXJrBdvNecvzQGjE0PT6JLg-yuolZfRplLvGoqmdeknssIXf7XZAp7FJUXlruW9lKLpINplpTfxvEjvLc1CW7ntyoAGQUHXCR8Ifot30gaYi9TuhRuRaYw5tafYJjMrJZCsaPXIDP_xda4XwLAvifWuu3S-ISF2HW0OrOigPjAzPc1vz6wTRDZS2kASHQa5DhQtzc_xsqJcyD0FYfFNqlWsEMdiIA_hHgXi327Xcsv0C3NqrmI5tkr0MljzZwElWrelBDudqdIS66-HxU8oNQDM4xpa-JJ13b9jy2y7vd23MA" \
  -H "Content-Type: application/json" \
  -d '{"name": "Jessica from Bumble"}' \
  "https://fdhf52udwe.execute-api.us-west-2.amazonaws.com/prod/connections"
  