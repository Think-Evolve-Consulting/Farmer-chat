# Kisan Chat - Authentication Setup

This guide explains how to set up Supabase authentication for the Kisan Chat application.

## Prerequisites

- A Supabase account (free tier available at https://supabase.com)
- Basic understanding of environment variables

## Step 1: Create a Supabase Project

1. Go to [https://app.supabase.com](https://app.supabase.com)
2. Sign up or log in to your account
3. Click "New Project"
4. Fill in the project details:
   - **Name**: Kisan Chat (or any name you prefer)
   - **Database Password**: Create a strong password (save it securely)
   - **Region**: Choose the closest region to your location
5. Click "Create new project" and wait for it to initialize (2-3 minutes)

## Step 2: Get API Keys

1. Once your project is ready, go to **Settings** > **API**
2. Copy the following values:
   - **Project URL** (under "Configuration")
   - **Anon (public) Key** (under "Project API keys")
3. Keep these values safe - you'll need them in the next step

## Step 3: Configure Environment Variables

1. In the `frontend` directory, create a file named `.env.local`
2. Copy the contents from `.env.example`
3. Replace the placeholders with your actual values:
   ```
   VITE_SUPABASE_URL=https://your-project-id.supabase.co
   VITE_SUPABASE_ANON_KEY=your_anon_key_here
   ```

## Step 4: Configure OAuth (Google Login)

### 4.1 Set Up Google OAuth Provider in Supabase

1. In your Supabase dashboard, go to **Authentication** > **Providers**
2. Find "Google" in the list and click it
3. Enable the provider by toggling the switch
4. You'll see a note about needing Google OAuth credentials

### 4.2 Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the "Google+ API":
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API"
   - Click "Enable"
4. Create OAuth 2.0 Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Web application"
   - Add authorized JavaScript origins:
     - `http://localhost:5173` (for local development)
     - `http://localhost:3000` (if using different port)
     - Your production domain (e.g., `https://kisanchat.example.com`)
   - Add authorized redirect URIs:
     - `http://localhost:5173/auth/callback`
     - Your production callback URL
   - Copy the Client ID and Client Secret

### 4.3 Add Google Credentials to Supabase

1. Back in your Supabase dashboard, under Authentication > Providers > Google
2. Paste your Google OAuth credentials:
   - **Client ID**: From Google Cloud Console
   - **Client Secret**: From Google Cloud Console
3. Click "Save"

## Step 5: Configure Authentication Methods

Your Supabase project automatically supports:
- **Email/Password Authentication**: Users can sign up and log in with email/password
- **Email Verification**: Optional email confirmation for new accounts
- **Google OAuth**: Users can sign in with their Google account

### Optional: Enable Email Confirmation

1. Go to **Authentication** > **Providers** > **Email**
2. Toggle "Confirm email" to require email verification
3. Customize the email template if desired

## Step 6: Test the Application

### Local Development

1. Make sure your `.env.local` file is set up correctly
2. Start the frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
3. Open http://localhost:5173 in your browser
4. You should see the login page
5. Test all auth methods:
   - Sign up with email/password
   - Log in with email/password
   - Log in with Google

### Troubleshooting

**Issue: "Supabase URL and key not found"**
- Ensure `.env.local` exists in the frontend directory with correct values
- Restart the dev server after creating/modifying `.env.local`

**Issue: "Invalid credentials" on login**
- Verify your Supabase URL and Anon Key are correct
- Check that email/password are correct

**Issue: Google login not working**
- Verify Google OAuth credentials are added to Supabase
- Check authorized redirect URIs in Google Cloud Console
- Ensure `http://localhost:5173/auth/callback` is in the redirect URIs

**Issue: "Redirect URL mismatch"**
- Add `http://localhost:5173/auth/callback` to your Google Cloud OAuth authorized redirect URIs
- Make sure the Supabase redirect URL settings match

## Security Notes

- ⚠️ **NEVER commit `.env.local` to version control**
- Keep your Anon Key public (it's meant for frontend use)
- Keep your Google OAuth credentials secret
- Validate all user input on both frontend and backend
- Use HTTPS in production

## Production Deployment

When deploying to production:

1. Update your `.env.local` (or environment variables) with production values
2. Add your production domain to Google OAuth authorized origins and redirects
3. Enable email confirmation for security
4. Set up proper CORS headers in your backend
5. Consider rate limiting for authentication endpoints

## File Structure

The authentication system is implemented across these files:

```
frontend/
├── src/
│   ├── contexts/
│   │   └── AuthContext.jsx       # Authentication context and hooks
│   ├── components/
│   │   ├── Login.jsx             # Login form component
│   │   ├── Signup.jsx            # Signup form component
│   │   ├── AuthCallback.jsx      # OAuth callback handler
│   │   ├── ProtectedRoute.jsx    # Route protection component
│   │   └── Header.jsx            # Updated with logout button
│   └── App.jsx                   # Updated with auth routing
├── .env.example            # Environment variable template
└── package.json                  # Updated with @supabase/supabase-js
```

## API Reference

### AuthContext

The `AuthContext` provides the following methods and state:

```javascript
import { useAuth } from './contexts/AuthContext';

function MyComponent() {
  const {
    user,                   // Currently logged-in user or null
    loading,               // Loading state during auth check
    error,                // Current error message
    signUp,               // Async: (email, password) => {success, data, error}
    signIn,               // Async: (email, password) => {success, data, error}
    signInWithGoogle,     // Async: () => {success, data, error}
    signOut,              // Async: () => {success, error}
    supabase,             // Direct Supabase client instance
  } = useAuth();

  // Usage example
  const handleLogin = async () => {
    const result = await signIn('user@example.com', 'password');
    if (result.success) {
      // User is logged in
    }
  };
}
```

## Next Steps

- Customize the login/signup UI to match your branding
- Add user profile page
- Implement password reset flow
- Set up email templates
- Add multi-factor authentication (MFA)
- Configure session management

## Support

For issues or questions:
- Check Supabase documentation: https://supabase.com/docs
- Visit Supabase GitHub: https://github.com/supabase/supabase
- Supabase Discord community: https://discord.supabase.com



