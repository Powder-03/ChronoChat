# Clerk Authentication Guide

## Overview

Clerk handles all authentication on the frontend. The backend validates JWT tokens from Clerk. This means:
- ✅ Email/Password login
- ✅ Google OAuth
- ✅ GitHub OAuth  
- ✅ Discord, Facebook, Twitter, LinkedIn, etc.
- ✅ Magic links
- ✅ SMS/OTP authentication

All authentication methods work **without backend changes** - just enable them in Clerk Dashboard!

## Enabling Google Authentication

### Step 1: Configure in Clerk Dashboard

1. Log in to [Clerk Dashboard](https://dashboard.clerk.com)
2. Select your application
3. Navigate to: **User & Authentication** → **Social Connections**
4. Find **Google** and toggle it ON

### Step 2: Choose OAuth Configuration

**Option A: Use Clerk's Shared Credentials (Easiest)**
- Clerk provides test OAuth credentials
- Good for development
- No additional setup needed
- Just toggle Google ON

**Option B: Use Your Own Google OAuth App (Production)**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Google+ API
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Set application type to "Web application"
6. Add authorized redirect URIs:
   ```
   https://accounts.clerk.dev/oauth_callback
   https://your-domain.com/oauth_callback
   ```
7. Copy Client ID and Client Secret
8. In Clerk Dashboard, select **Use custom credentials**
9. Paste your Google OAuth credentials

### Step 3: Frontend Integration

No backend changes needed! Just integrate Clerk in your frontend:

#### React/Next.js Example

```bash
npm install @clerk/nextjs
# or
npm install @clerk/clerk-react
```

**app/layout.tsx (Next.js App Router):**
```tsx
import { ClerkProvider } from '@clerk/nextjs'

export default function RootLayout({ children }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  )
}
```

**Sign In Component:**
```tsx
import { SignIn } from '@clerk/nextjs'

export default function SignInPage() {
  return <SignIn />
}
```

That's it! The `<SignIn />` component automatically shows all enabled authentication methods including Google.

#### Making Authenticated API Calls

```tsx
import { useAuth } from '@clerk/nextjs'

function ChatComponent() {
  const { getToken } = useAuth()
  
  const sendMessage = async (message: string) => {
    const token = await getToken()
    
    const response = await fetch('http://localhost:8000/api/chat/message', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    })
    
    return response.json()
  }
  
  return (
    // Your chat UI
  )
}
```

## Testing Google Authentication

1. Start your backend:
   ```bash
   docker-compose up
   ```

2. In your frontend, click "Sign in with Google"

3. Authenticate with Google

4. Clerk generates a JWT token

5. Use the token to call protected endpoints:
   ```bash
   curl -H "Authorization: Bearer <CLERK_TOKEN>" \
        http://localhost:8000/api/auth/me
   ```

## Other OAuth Providers

Enable the same way in Clerk Dashboard:

### Popular Providers Supported:
- **GitHub** - Great for developer tools
- **Microsoft** - For enterprise apps
- **Discord** - For gaming/community apps
- **Facebook** - Wide user base
- **Twitter/X** - Social integration
- **LinkedIn** - Professional networks
- **Apple** - iOS apps

### Enterprise SSO (Paid Plans):
- SAML
- Azure AD
- Okta
- Google Workspace

## Security Notes

### Backend Token Verification

The backend automatically verifies:
- ✅ Token signature (using Clerk's public key)
- ✅ Token expiration
- ✅ Token issuer
- ✅ Token claims

This is handled in `app/core/clerk.py`:

```python
async def verify_token(self, token: str):
    payload = jwt.decode(
        token,
        self.jwt_key,
        algorithms=["RS256"],
        options={"verify_signature": True}
    )
    return payload
```

### User Information

After Google authentication, you can access:
- User ID (unique identifier)
- Email address
- Name
- Profile picture
- Google account metadata

All available via Clerk's API:
```python
user_info = await clerk_auth.get_user_info(user_id)
```

## Customization

### Custom OAuth Button Styling

In your frontend:
```tsx
<SignIn 
  appearance={{
    elements: {
      socialButtonsBlockButton: "custom-google-button-class",
      formButtonPrimary: "custom-primary-button"
    }
  }}
/>
```

### Redirect After Sign In

```tsx
<SignIn 
  redirectUrl="/dashboard"
  afterSignInUrl="/dashboard"
/>
```

### Require Specific Auth Methods

In Clerk Dashboard:
- Toggle OFF methods you don't want
- Reorder authentication options
- Set primary authentication method

## Troubleshooting

### Google Sign In Not Showing
- Verify Google is enabled in Clerk Dashboard
- Clear browser cache
- Check browser console for errors

### Token Validation Fails
- Ensure `CLERK_JWT_KEY` is correct in `.env`
- Verify it's the PEM public key from JWT Template
- Check token hasn't expired

### Backend Can't Verify Token
- Confirm `CLERK_SECRET_KEY` is correct
- Make sure token is sent as `Bearer <token>`
- Check network connectivity to Clerk API

## Resources

- [Clerk Documentation](https://clerk.com/docs)
- [Clerk Social OAuth Guide](https://clerk.com/docs/authentication/social-connections/google)
- [Google OAuth Setup](https://developers.google.com/identity/protocols/oauth2)
- [Clerk React SDK](https://clerk.com/docs/references/react/overview)
- [Clerk Next.js SDK](https://clerk.com/docs/references/nextjs/overview)
