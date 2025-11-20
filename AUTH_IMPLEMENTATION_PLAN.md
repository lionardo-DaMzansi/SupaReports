# Authentication & User Management Implementation Plan

## Overview
Complete user authentication system with email verification, session management, activity tracking, and admin monitoring.

## Database Schema

### 1. Users Table
```sql
- id (PRIMARY KEY)
- email (UNIQUE, NOT NULL)
- password_hash (NOT NULL)
- username (UNIQUE)
- verified (BOOLEAN, default FALSE)
- verification_token (STRING)
- profile_picture (STRING, path to image or default avatar)
- created_at (DATETIME)
- last_login (DATETIME)
```

### 2. Sessions Table
```sql
- id (PRIMARY KEY)
- user_id (FOREIGN KEY -> Users.id)
- session_token (UNIQUE, NOT NULL)
- created_at (DATETIME)
- last_active (DATETIME)
- ip_address (STRING)
- user_agent (STRING)
- is_active (BOOLEAN, default TRUE)
```

### 3. ActivityLogs Table
```sql
- id (PRIMARY KEY)
- user_id (FOREIGN KEY -> Users.id)
- action_type (STRING) # 'audio_generated', 'video_generated', 'email_sent', 'analysis_processed', 'report_generated'
- timestamp (DATETIME)
- details (JSON) # Additional metadata
- resource_id (STRING) # ID of created resource if applicable
```

### 4. UserStats Table
```sql
- user_id (PRIMARY KEY, FOREIGN KEY -> Users.id)
- reports_count (INTEGER, default 0)
- audio_count (INTEGER, default 0)
- video_count (INTEGER, default 0)
- emails_sent_count (INTEGER, default 0)
- analyses_count (INTEGER, default 0)
- last_updated (DATETIME)
```

## Features Implementation

### 1. Sign Up Flow
**Route:** `POST /api/auth/signup`

**Process:**
1. Validate email format and uniqueness
2. Hash password with bcrypt
3. Generate verification token
4. Create user record (verified=FALSE)
5. Send verification email
6. Return success message

**Email Verification:**
- Route: `GET /api/auth/verify/<token>`
- Validates token, sets verified=TRUE
- Redirects to login page

### 2. Sign In Flow
**Route:** `POST /api/auth/login`

**Process:**
1. Validate email + password
2. Check if email is verified
3. Check for existing active session
4. If active session exists → block login (enforce one session rule)
5. Generate session token
6. Create session record
7. Set cookie/return token
8. Update last_login timestamp

### 3. Session Management

**One Session Per User Rule:**
- Before creating new session, check Sessions table for active sessions
- If active session found:
  - Option A: Block new login, return error
  - Option B: Invalidate old session, create new one (configurable)

**Session Validation Middleware:**
```python
@login_required
def protected_route():
    # Validates session token
    # Updates last_active timestamp
    # Returns 401 if invalid/expired
```

**Session Timeout:**
- Sessions expire after 24 hours of inactivity
- Cleanup job runs periodically

### 4. Profile Picture Management

**Default Avatars (5 options):**
```
/static/avatars/default-1.png
/static/avatars/default-2.png
/static/avatars/default-3.png
/static/avatars/default-4.png
/static/avatars/default-5.png
```

**Upload Route:** `POST /api/user/profile-picture`
- Accepts image file
- Validates format (JPG, PNG)
- Resizes to 200x200px
- Saves to `/static/uploads/profiles/<user_id>.png`
- Updates user.profile_picture field

### 5. Activity Logging

**Logged Actions:**
1. **Audio Generated** - When TTS creates audio (Panel 3)
2. **Video Generated** - When lipsync video created (Panel 4)
3. **Email Sent** - When email sent (Panel 5)
4. **Analysis Processed** - When dashboard analysis completes (Panel 2)
5. **Report Generated** - When video is generated (counts as report)

**Implementation:**
```python
def log_activity(user_id, action_type, details=None):
    log = ActivityLog(
        user_id=user_id,
        action_type=action_type,
        timestamp=datetime.utcnow(),
        details=json.dumps(details) if details else None
    )
    db.session.add(log)

    # Update user stats
    update_user_stats(user_id, action_type)
    db.session.commit()
```

**Where to Add Logging:**
- `app.py` line ~1450: After audio generation (ElevenLabs)
- `app.py` line ~1600: After video generation (TopView)
- `app.py` line ~900: After email sent
- `app.py` line ~1050: After analysis completion
- Count report when video is generated

### 6. Frontend UI Changes

**Login/Signup Modal:**
```html
<div id="authModal" class="modal">
    <div class="modal-content">
        <div id="loginForm">...</div>
        <div id="signupForm" style="display: none;">...</div>
    </div>
</div>
```

**Header Updates:**
```html
<div class="logo">
    <div class="logo-title">SUPA REPORTS</div>
</div>

<div class="user-profile" id="userProfile">
    <div class="user-avatar">
        <img src="/static/uploads/profiles/user_123.png">
    </div>
    <div class="user-info">
        <div class="user-name">John Doe</div>
        <div class="user-stats">
            <span>📊 Reports: 12</span>
            <span>🎤 Audio: 15</span>
            <span>🎬 Videos: 12</span>
        </div>
    </div>
</div>

<div class="global-stats">
    <span>🟢 Live Sessions: 5</span>
</div>
```

### 7. Dashboard Access Protection

**Middleware:**
```python
@app.before_request
def require_auth():
    public_routes = ['/api/auth/login', '/api/auth/signup', '/api/auth/verify']
    if request.path not in public_routes:
        if not current_user.is_authenticated:
            return redirect('/login')
        if not current_user.verified:
            return jsonify({'error': 'Email not verified'}), 403
```

**Looker Studio Dashboard:**
- Only accessible after authentication
- Check verified=TRUE before showing dashboard

### 8. Admin Dashboard

**Route:** `GET /admin/dashboard`

**Access Control:**
- Only for admin users (add is_admin field to Users table)
- Or password-protected page

**Display Data:**

**Overall Stats:**
```
Total Users: 150
Active Sessions: 12
Total Reports: 1,234
Total Audio: 1,450
Total Videos: 1,234
Total Emails: 980
Total Analyses: 567
```

**User Breakdown Table:**
```
| User          | Sessions | Reports | Audio | Videos | Emails | Analyses |
|---------------|----------|---------|-------|--------|--------|----------|
| john@email.com| 5        | 23      | 30    | 23     | 18     | 15       |
| jane@email.com| 3        | 12      | 15    | 12     | 10     | 8        |
```

**Activity Timeline:**
```
2024-11-09 14:30 | john@email.com  | VIDEO_GENERATED
2024-11-09 14:25 | jane@email.com  | AUDIO_GENERATED
2024-11-09 14:20 | john@email.com  | EMAIL_SENT
```

**Filters:**
- Date range
- User
- Action type
- Export to CSV

## Implementation Steps

### Phase 1: Database & Models
1. Create `models.py` with all database models
2. Initialize SQLAlchemy in `app.py`
3. Create database tables

### Phase 2: Authentication Backend
1. Add Flask-Login setup to `app.py`
2. Create authentication routes:
   - `/api/auth/signup`
   - `/api/auth/login`
   - `/api/auth/logout`
   - `/api/auth/verify/<token>`
3. Add session management logic
4. Email verification with Flask-Mail

### Phase 3: Frontend UI
1. Create login/signup modal
2. Update header with user profile
3. Add global stats display
4. Profile picture upload form

### Phase 4: Activity Logging
1. Create `log_activity()` function
2. Add logging to all key actions
3. Update user stats automatically

### Phase 5: Admin Dashboard
1. Create admin template
2. Add stats queries
3. User activity table
4. Export functionality

### Phase 6: Testing & Security
1. Test one-session-per-user enforcement
2. Test email verification flow
3. Security audit (SQL injection, XSS, CSRF)
4. Rate limiting on auth endpoints

## Environment Variables Needed

Add to `.env`:
```
# Database
DATABASE_URL=sqlite:///supa_reports.db

# Flask Secret Key
SECRET_KEY=your-secret-key-here

# Email Configuration (for verification emails)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=supachatglobal@gmail.com
MAIL_PASSWORD=nwyhpclsknnwsbhr
MAIL_DEFAULT_SENDER=supachatglobal@gmail.com

# Session Settings
SESSION_COOKIE_SECURE=False  # Set True in production with HTTPS
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=86400  # 24 hours
```

## Security Considerations

1. **Password Security:**
   - Use bcrypt with cost factor 12+
   - Enforce minimum password length (8 chars)
   - Optional: Password complexity requirements

2. **Session Security:**
   - Secure session tokens (use secrets.token_urlsafe(32))
   - HttpOnly cookies
   - CSRF protection
   - Session timeout after inactivity

3. **Rate Limiting:**
   - Login attempts: 5 per 15 minutes
   - Signup attempts: 3 per hour
   - Email verification resends: 3 per hour

4. **Email Verification:**
   - Tokens expire after 24 hours
   - One-time use tokens

5. **SQL Injection Prevention:**
   - Use SQLAlchemy ORM (parameterized queries)
   - Never concatenate user input into SQL

6. **XSS Prevention:**
   - Escape all user input in templates
   - Content Security Policy headers

## Monitoring & Analytics

**Key Metrics to Track:**
1. Daily Active Users (DAU)
2. Reports generated per day
3. Average resources per user
4. Peak usage times
5. Failed login attempts
6. Email verification rate

**Cost Analysis:**
- Audio generation cost per user
- Video generation cost per user
- Email sending cost per user
- Total monthly cost breakdown

## Future Enhancements

1. **Password Reset Flow**
2. **Two-Factor Authentication (2FA)**
3. **OAuth Integration** (Google, Microsoft)
4. **API Rate Limiting** per user
5. **User Roles** (admin, power user, basic)
6. **Team/Organization** support
7. **Usage Quotas** (X reports per month)
8. **Billing Integration** (Stripe)

---

## File Structure

```
/Users/willpandle/supachat-azi-local/
├── app.py (updated with auth routes)
├── models.py (new - database models)
├── auth.py (new - authentication logic)
├── admin.py (new - admin dashboard)
├── supa_reports.db (new - SQLite database)
├── static/
│   ├── avatars/ (new)
│   │   ├── default-1.png
│   │   ├── default-2.png
│   │   ├── default-3.png
│   │   ├── default-4.png
│   │   └── default-5.png
│   ├── uploads/ (new)
│   │   └── profiles/
│   └── index.html (updated with auth UI)
└── templates/ (new)
    ├── login.html
    ├── signup.html
    └── admin_dashboard.html
```

---

This is a comprehensive authentication system that will provide full user management, activity tracking, and admin monitoring capabilities for Supa Reports!
