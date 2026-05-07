# FitAvatar Backend — Database Connection Troubleshooting Guide

## The Error: "Profile Sync error: Backend error: Internal Server Error"

### Root Cause
```
psycopg2.OperationalError: connection to server at "aws-0-ap-south-1.pooler.supabase.com" (3.108.251.216), 
port 6543 failed: FATAL: (ENOTFOUND) tenant/user postgres.puijhryopijblwokqcjd not found
```

This error occurs when:
1. The `DATABASE_URL` environment variable is incorrect, malformed, or missing
2. The Supabase project has been deleted or suspended
3. The database credentials (username/password) are wrong
4. The Supabase project ID is incorrect

---

## Solution: Verify Your DATABASE_URL on Render

### Step 1: Get Your Supabase Connection String

1. Go to **Supabase Dashboard** → Your Project
2. Click **Settings** → **Database**
3. Look for **Connection string** (NOT connection pooler)
4. Scroll down to find the **Transaction Pooler** connection string
5. Copy the connection string that looks like this:

```
postgresql://postgres.YOUR_PROJECT_ID:YOUR_PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres
```

### Step 2: Update DATABASE_URL on Render

1. Go to **Render Dashboard** → Your Service (fitavatar-api)
2. Click **Environment** (in the left sidebar)
3. Find the `DATABASE_URL` variable
4. **Replace it** with your Supabase connection string from Step 1
5. Click **Save Changes**

**Important Details:**
- **Use Transaction Pooler** (port 6543) — NOT Connection Pooler (port 5432)
- **Format:** `postgresql://postgres.PROJECT_ID:PASSWORD@aws-REGION.pooler.supabase.com:6543/postgres`
- **Example:**
  ```
  postgresql://postgres.abcdefgh123456:MySecurePassword123!@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
  ```

### Step 3: Redeploy on Render

1. Go to **Render Dashboard** → Your Service
2. Click the **"Deploy" button** (or **redeploy** if it already deployed)
3. Wait for the deployment to complete
4. Check the **Logs** for any errors

---

## Verify the Connection Works

### Check Server Logs After Deployment

After redeploy, look for these success messages in the Render logs:

```
[FitAvatar API] Starting up...
[FitAvatar API] Database connection successful.
[FitAvatar API] Database tables verified.
[FitAvatar API] ML model loaded.
INFO: Uvicorn running on http://0.0.0.0:10000
```

### Test the API

Once deployed, test the connection:

```bash
# Health check
curl https://fitavatar-api.onrender.com/

# Should return 200 OK
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using Connection Pooler (port 5432) | Use **Transaction Pooler (port 6543)** |
| Missing project ID | Get it from Supabase Dashboard → Settings → General |
| Wrong password | Copy from Supabase → Settings → Database → Reset Database Password |
| Old/deleted project | Create a new Supabase project and get new credentials |
| Typo in connection string | Double-check: `postgresql://`, `@aws-`, `.pooler.supabase.com:6543` |
| Not redeploying after change | Always click **Deploy** after changing env vars |

---

## Format Breakdown

```
postgresql://postgres.PROJECT_ID:PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres
         │  │                                                         │
      Scheme │                                                    Port 6543
             └─ Always use "postgres." prefix for transaction pooler
```

---

## If You're Still Getting Errors

### 1. Verify Supabase Project Exists
- Log in to Supabase Dashboard
- Check if your project is listed and **not suspended**
- If suspended, you need to upgrade your plan

### 2. Check Firewall Rules
- Render needs to connect to Supabase on port 6543
- Supabase should allow all IPs (it does by default)

### 3. Test Locally (Optional)
```python
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres.YOUR_PROJECT_ID:YOUR_PASSWORD@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"

engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("Connection successful!")
```

### 4. Check Render Service Logs
In Render Dashboard, go to your service and check:
- **Logs** tab (real-time logs)
- **Events** tab (deployment history)
- Look for specific error messages

---

## Environment Variables Needed on Render

| Variable | Value | Example |
|----------|-------|---------|
| `DATABASE_URL` | Supabase transaction pooler URL | `postgresql://postgres.xyz:pass@aws-0-ap-south-1.pooler.supabase.com:6543/postgres` |
| `SUPABASE_JWT_SECRET` | Your Supabase JWT secret | (from Supabase Settings) |
| `AUTO_CREATE_TABLES` | `true` (on first deploy) | `true` |

---

## After Fixing DATABASE_URL

The backend will:
1. ✅ Test the connection on startup
2. ✅ Create database tables automatically (if `AUTO_CREATE_TABLES=true`)
3. ✅ Reject requests with a 503 error if connection fails (instead of crashing)
4. ✅ Provide better error messages for debugging

---

## Still Need Help?

Check the error message in Render logs carefully:
- `"tenant/user ... not found"` → Wrong credentials or project ID
- `"connection refused"` → Network issue or wrong port
- `"could not connect"` → Supabase server unreachable
- `"FATAL: password authentication failed"` → Wrong password

Contact support with the full error message from Render logs.
