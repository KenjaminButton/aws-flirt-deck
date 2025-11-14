

# Problem 1: Auto-logout on token expiry
You're right! Currently when the token expires, API calls fail with 401 but the user stays "logged in" on the frontend. This is confusing.
Solution approach:

Add an Axios/fetch interceptor in your API client
When ANY request returns 401, automatically:

Clear tokens from localStorage
Redirect to login page
Show a toast: "Session expired, please log in again"

This is a common pattern and pretty straightforward to implement.


# Problem 2: Settings page content


### Keep in mind that there is a billings tab in the NavBar component. Should we get rid of the billings tab in the navbar component then?

For MVP, I'd suggest keep it minimal:
Essential:

Account info (email, name - read-only)
Subscription status (Free/Premium)
"Cancel Subscription" button (if premium)

Nice to have (but maybe overkill for MVP):

Change password
Delete account
Notification preferences

My recommendation: Just do subscription management for now. Settings page with:

"Your Plan: Free" or "Your Plan: Premium ($2.99/month)"
If premium: "Cancel Subscription" button → calls Stripe API to cancel
If free: "Upgrade to Premium" button

Keep it simple!



# Problem 3: Contact/Support
Good idea! For MVP, simplest approach:
Option A - Email link in footer:
Questions? Email us at support@flirtdeck.com
Option B - Contact page with:

Simple form (name, email, message)
Sends email via AWS SES (or just mailto: link)

My recommendation: Start with just an email link in the footer/navbar. No need for a whole contact form system for MVP.






1. Finish up the details of the app and then switch to a new Claude conversation





## Future Stretch Features:

1. Export conversation history to a PDF
2. Apple login
3. 
