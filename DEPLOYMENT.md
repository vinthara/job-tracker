# Deployment Guide - Job Tracker

Deploy Job Search Tracker to an Ubuntu/Debian server with systemd + nginx.

## Prerequisites

- Ubuntu 22.04+ or Debian 12+
- Domain name `candidatures.aralyra.com` pointing to your server
- Root/sudo access

## Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y nginx certbot python3-certbot-nginx git

# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

## Step 2: Clone the Application

```bash
cd ~/perso
# If not already cloned
git clone <your-repo-url> job-tracker
cd job-tracker

# Install dependencies
uv sync

# Initialize database
uv run python -c "from models import init_db; init_db()"
```

## Step 3: Configure Google OAuth

### 3.1 Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable Google+ API:
   - APIs & Services → Library
   - Search "Google+ API" → Enable
4. Create OAuth 2.0 Credentials:
   - APIs & Services → Credentials
   - Create Credentials → OAuth 2.0 Client ID
   - Application type: Web application
   - Name: Job Tracker
   - Authorized redirect URIs:
     - `https://candidatures.aralyra.com/oauth2callback`
     - `http://localhost:8502/oauth2callback` (for local testing)
   - Save the Client ID and Client Secret

### 3.2 Configure Secrets

```bash
cd ~/perso/job-tracker

# Create secrets file from example
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
nano .streamlit/secrets.toml
```

Update these values:
```toml
[auth]
redirect_uri = "https://candidatures.aralyra.com/oauth2callback"
cookie_secret = "generate-random-string-here"  # Use: python3 -c "import secrets; print(secrets.token_urlsafe(32))"
client_id = "your-client-id.apps.googleusercontent.com"
client_secret = "GOCSPX-your-client-secret"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
allowed_emails = "your-email@gmail.com,other-email@gmail.com"
```

## Step 4: Setup Systemd Service

```bash
# Edit service file with your username
nano job-tracker.service
# Replace YOUR_USERNAME with: aravinth

# Copy to systemd
sudo cp job-tracker.service /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable job-tracker
sudo systemctl start job-tracker

# Check status
sudo systemctl status job-tracker
```

## Step 5: Setup Nginx

```bash
# Copy nginx config
sudo cp nginx-job-tracker.conf /etc/nginx/sites-available/job-tracker
sudo ln -s /etc/nginx/sites-available/job-tracker /etc/nginx/sites-enabled/

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

## Step 6: SSL Certificate (Let's Encrypt)

```bash
sudo certbot --nginx -d candidatures.aralyra.com
```

Follow the prompts. Certbot will automatically configure SSL.

## Step 7: Firewall

```bash
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## Testing

Visit: `https://candidatures.aralyra.com`

You should see:
1. Login page with "Log in with Google" button
2. After clicking, Google OAuth login flow
3. After successful login, the job tracker dashboard

## Useful Commands

```bash
# View logs
sudo journalctl -u job-tracker -f

# Restart service
sudo systemctl restart job-tracker

# Check nginx logs
sudo tail -f /var/log/nginx/error.log

# Check if app is running
curl http://127.0.0.1:8502
```

## Troubleshooting

### Service won't start
- Check logs: `sudo journalctl -u job-tracker -e`
- Verify paths in service file
- Check uv is installed: `which uv`
- Verify database exists: `ls -la ~/perso/job-tracker/job_tracker.db`

### OAuth redirect error
- Verify redirect_uri in `.streamlit/secrets.toml` matches Google Cloud Console
- Must use HTTPS in production
- Check allowed redirect URIs in Google Cloud Console

### 502 Bad Gateway
- Check if Streamlit is running: `sudo systemctl status job-tracker`
- Check nginx config: `sudo nginx -t`
- Check port 8502 is listening: `ss -tlnp | grep 8502`

### Access Denied after login
- Check email is in `allowed_emails` list in secrets.toml
- Verify email format (no extra spaces)

### Database errors
- Ensure database file has correct permissions
- Check working directory in systemd service

## File Checklist

- [x] `nginx-job-tracker.conf` - Nginx reverse proxy config
- [x] `job-tracker.service` - Systemd service file
- [x] `.streamlit/secrets.toml` - OAuth credentials (create from example)
- [x] `job_tracker.db` - SQLite database
- [x] `app.py` - Main application (with Google auth)

## Security Notes

1. **Never commit `.streamlit/secrets.toml`** - It's in `.gitignore`
2. **Use HTTPS in production** - Google OAuth requires it
3. **Keep `client_secret` private** - Never share or expose it
4. **Use a strong `cookie_secret`** - Random string, 32+ characters
5. **Limit `allowed_emails`** - Only add trusted users
