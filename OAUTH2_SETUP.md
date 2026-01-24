# Google OAuth2 Setup Guide

Step-by-step guide to configure Google authentication for Job Tracker.

## Why Google OAuth?

1. **Secure**: Your app never sees the user's Google password
2. **Easy**: Users don't need to create another account
3. **Trusted**: Users trust Google's login page
4. **Control**: You control who can access via email whitelist

## Step 1: Google Cloud Console Setup

### 1.1 Create/Select Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project" or select existing project
4. Name: `Job Tracker` (or your preferred name)
5. Click "Create"

### 1.2 Enable Google+ API

1. In the left sidebar: **APIs & Services** → **Library**
2. Search for: `Google+ API`
3. Click on it and press **Enable**
4. Wait for it to activate

### 1.3 Create OAuth 2.0 Credentials

1. Go to: **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **OAuth 2.0 Client ID**
3. If prompted, configure the OAuth consent screen:
   - User Type: **External** (or Internal if using Google Workspace)
   - App name: `Job Tracker`
   - User support email: Your email
   - Developer contact: Your email
   - Click **Save and Continue**
   - Scopes: Skip (default is fine)
   - Test users: Add your email
   - Click **Save and Continue**

4. Create OAuth Client ID:
   - Application type: **Web application**
   - Name: `Job Tracker`
   - Authorized redirect URIs - click **+ Add URI**:
     - For local dev: `http://localhost:8502/oauth2callback`
     - For production: `https://candidatures.aralyra.com/oauth2callback`
   - Click **Create**

5. **Save the credentials:**
   - Copy the **Client ID** (ends with `.apps.googleusercontent.com`)
   - Copy the **Client Secret** (starts with `GOCSPX-`)
   - Keep these safe!

## Step 2: Configure Local Secrets

```bash
cd ~/perso/job-tracker

# Create secrets file from example
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edit the file
nano .streamlit/secrets.toml
```

Fill in these values:

```toml
[auth]
# For local development
redirect_uri = "http://localhost:8502/oauth2callback"

# Generate a random cookie secret
# Run: python3 -c "import secrets; print(secrets.token_urlsafe(32))"
cookie_secret = "PASTE_RANDOM_STRING_HERE"

# From Google Cloud Console
client_id = "YOUR_CLIENT_ID.apps.googleusercontent.com"
client_secret = "GOCSPX-YOUR_CLIENT_SECRET"

# Don't change this
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

# Your email address(es) - comma separated
allowed_emails = "your-email@gmail.com"
```

### Generate Cookie Secret

Run this command to generate a secure random string:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and paste it as the `cookie_secret` value.

## Step 3: Test Locally

```bash
cd ~/perso/job-tracker

# Run the app
uv run streamlit run app.py --server.port 8502

# Open browser to: http://localhost:8502
```

You should see:
1. **Login page** with "Log in with Google" button
2. Click the button → **Google login flow**
3. Sign in with your Google account
4. Grant permissions
5. Redirected back to **Job Tracker dashboard**

## Step 4: Production Setup

When deploying to `candidatures.aralyra.com`:

### 4.1 Update secrets.toml on server

```toml
[auth]
# Use HTTPS for production
redirect_uri = "https://candidatures.aralyra.com/oauth2callback"

# Same cookie secret (or generate new one)
cookie_secret = "your-random-string"

# Same Google credentials
client_id = "YOUR_CLIENT_ID.apps.googleusercontent.com"
client_secret = "GOCSPX-YOUR_CLIENT_SECRET"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

# List of allowed emails
allowed_emails = "user1@gmail.com,user2@gmail.com"
```

### 4.2 Update Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. **APIs & Services** → **Credentials**
3. Click on your OAuth 2.0 Client ID
4. Add production redirect URI:
   - `https://candidatures.aralyra.com/oauth2callback`
5. Click **Save**

## Troubleshooting

### Error: "redirect_uri_mismatch"

**Problem:** The redirect URI doesn't match what's in Google Cloud Console

**Solution:**
1. Check `.streamlit/secrets.toml` - copy the exact `redirect_uri`
2. Go to Google Cloud Console → Credentials
3. Make sure this exact URI is in "Authorized redirect URIs"
4. Include the protocol (`http://` or `https://`)
5. Include the port for localhost (`:8502`)
6. Must end with `/oauth2callback`

### Error: "Access Denied" after login

**Problem:** Your email is not in the allowed list

**Solution:**
1. Check `.streamlit/secrets.toml`
2. Verify your email is in `allowed_emails`
3. No extra spaces: `"email1@gmail.com,email2@gmail.com"`
4. Restart the app after changing secrets.toml

### Login loop (keeps redirecting)

**Problem:** Cookie not being saved

**Solution:**
1. Verify `cookie_secret` is set in secrets.toml
2. Clear browser cookies and try again
3. Check browser console for errors
4. Try incognito/private mode

### Local development: "This app isn't verified"

**Problem:** Google shows warning for test apps

**Solution:**
1. This is normal for development
2. Click "Advanced" → "Go to Job Tracker (unsafe)"
3. Or add yourself as a test user in Google Cloud Console

### Production: SSL/HTTPS errors

**Problem:** OAuth requires HTTPS in production

**Solution:**
1. Set up SSL certificate with Let's Encrypt (see DEPLOYMENT.md)
2. Ensure `redirect_uri` uses `https://`
3. Force HTTPS in nginx config (already configured)

## Security Best Practices

1. ✅ **Never commit** `.streamlit/secrets.toml` - it's in `.gitignore`
2. ✅ **Use HTTPS** in production - Google requires it
3. ✅ **Keep client_secret private** - treat it like a password
4. ✅ **Generate strong cookie_secret** - use the command above
5. ✅ **Limit allowed_emails** - only add users you trust
6. ✅ **Rotate secrets** if compromised - generate new credentials in Google Cloud Console

## Adding More Users

To allow more people to access the app:

1. Edit `.streamlit/secrets.toml`
2. Add their email to `allowed_emails`:
   ```toml
   allowed_emails = "user1@gmail.com,user2@gmail.com,user3@example.com"
   ```
3. Restart the app:
   ```bash
   # Local
   Ctrl+C and restart streamlit

   # Production
   sudo systemctl restart job-tracker
   ```

Users will need a Google account with that email address to login.

## Complete Flow Diagram

```
┌──────────┐     ┌──────────────┐     ┌──────────┐
│   User   │────>│  Job Tracker │────>│  Google  │
└──────────┘     └──────────────┘     └──────────┘
     │                  │                    │
     │ 1. Visit app     │                    │
     │──────────────────>                    │
     │                  │                    │
     │ 2. See login page│                    │
     │<─────────────────│                    │
     │                  │                    │
     │ 3. Click "Login with Google"         │
     │──────────────────>                    │
     │                  │ 4. Redirect         │
     │                  │────────────────────>│
     │ 5. Google login page                  │
     │<──────────────────────────────────────│
     │                  │                    │
     │ 6. Enter credentials & approve        │
     │───────────────────────────────────────>│
     │                  │ 7. Auth code        │
     │                  │<────────────────────│
     │                  │ 8. Exchange for     │
     │                  │    user info        │
     │                  │────────────────────>│
     │                  │<────────────────────│
     │                  │                    │
     │                  │ 9. Check email in  │
     │                  │    allowed_emails  │
     │                  │                    │
     │ 10. Show dashboard if authorized      │
     │<─────────────────│                    │
```

## Need Help?

- Google Cloud Console: https://console.cloud.google.com/
- OAuth 2.0 Docs: https://developers.google.com/identity/protocols/oauth2
- Streamlit Auth Docs: https://docs.streamlit.io/
