# Admin Credentials Now Stored in Database

## ✅ MIGRATION COMPLETE

Admin authentication credentials are now stored in MongoDB database instead of environment variables. This provides better security, flexibility, and management capabilities.

---

## What Changed

### Before:
- Admin email and password stored in `.env` file
- `ADMIN_EMAIL=admin@chillicare.com`
- `ADMIN_PASSWORD=admin123`
- Admin user had special handling (not stored in database)
- Admin couldn't be managed like regular users

### After:
- Admin credentials stored in MongoDB `users` collection
- Admin user has `user_type: 'admin'`
- Password hashed with bcrypt (secure)
- Admin can be managed, updated, or promoted
- No special handling needed in code
- Multiple admins can be created

---

## How to Create Admin User

### Method 1: Using the Admin Creation Script (Recommended)

```bash
python create_admin.py
```

**Interactive Options:**
1. Create/Update admin user
2. Show existing admin users
3. Exit

**Default Admin Credentials:**
- Email: `admin@chillicare.com`
- Password: `admin123`

**Custom Admin Credentials:**
- Choose "no" when asked about default credentials
- Enter custom email and password
- Password must be at least 6 characters

### Method 2: Using MongoDB Directly

```javascript
// In MongoDB shell or Compass
db.users.insertOne({
  email: "admin@chillicare.com",
  password: "$2b$12$..." // bcrypt hash of your password
  user_type: "admin",
  created_at: new Date(),
  last_login: null
})
```

---

## Admin Login

Admin users now login exactly like regular users:

**Endpoint:** `POST /api/auth/login`

**Request Body:**
```json
{
  "email": "admin@chillicare.com",
  "password": "admin123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": "65f...",
    "email": "admin@chillicare.com",
    "user_type": "admin"
  }
}
```

---

## Database Schema

### Users Collection

Admin users are stored with the same schema as regular users:

```json
{
  "_id": ObjectId("..."),
  "email": "admin@chillicare.com",
  "password": "$2b$12$hashed_password_here",
  "user_type": "admin",  // ← Key difference
  "created_at": ISODate("2026-03-09T..."),
  "last_login": ISODate("2026-03-09T...")
}
```

**User Types:**
- `farmer` - Regular users
- `admin` - Administrator users

---

## Admin Management Features

### Create Admin
```bash
python create_admin.py
# Choose option 1
```

### Show All Admins
```bash
python create_admin.py
# Choose option 2
```

Or query database directly:
```javascript
db.users.find({ user_type: "admin" })
```

### Update Admin Password
```bash
python create_admin.py
# If admin exists, you'll be prompted to update password
```

### Promote User to Admin

Using the script:
```bash
python create_admin.py
# Enter existing user's email
# Script will detect user exists and offer to promote
```

Using MongoDB:
```javascript
db.users.updateOne(
  { email: "user@example.com" },
  { $set: { user_type: "admin" } }
)
```

### Create Multiple Admins

Repeat the creation process with different emails:
```bash
python create_admin.py
# Use custom credentials
# Email: admin2@chillicare.com
# Password: custom_password
```

---

## Code Changes Summary

### app.py Changes:

1. **Removed Environment Variables:**
   ```python
   # Before:
   ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@chillicare.com')
   ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
   
   # After:
   # (Removed - no longer needed)
   ```

2. **Updated load_user Function:**
   ```python
   # Before: Special handling for admin (id='admin')
   if user_id == 'admin':
       return User('admin', ADMIN_EMAIL, 'admin')
   
   # After: All users loaded from database
   user_data = mongodb.get_user_by_id(user_id)
   if user_data:
       return User(str(user_data['_id']), user_data['email'], user_data['user_type'])
   ```

3. **Updated login Function:**
   ```python
   # Before: Special admin login logic with env variables
   if email == ADMIN_EMAIL.lower():
       if password == ADMIN_PASSWORD:
           # Special admin handling
   
   # After: Unified login for all users
   user_data = mongodb.get_user_by_email(email)
   if bcrypt.checkpw(password, user_data['password']):
       # Same process for admin and farmer
   ```

4. **Updated signup Function:**
   ```python
   # Before: Prevented signup with admin email
   if email == ADMIN_EMAIL.lower():
       return error
   
   # After: No special admin email check
   # (Admin users created via create_admin.py)
   ```

5. **Updated health_check Function:**
   ```python
   # Before:
   'admin_configured': bool(ADMIN_EMAIL and ADMIN_PASSWORD)
   
   # After:
   'admin_stored_in_db': True
   ```

---

## Security Improvements

### 1. Password Security
- Admin passwords now hashed with bcrypt (same as all users)
- Passwords never stored in plain text
- No passwords in environment variables or config files

### 2. Audit Trail
- Admin login/logout tracked in logs
- Last login timestamp recorded
- User creation timestamp preserved

### 3. Access Control
- Admin users identified by `user_type` field
- Protected endpoints check user_type
- Admin accounts cannot be deleted via API

### 4. Multiple Admins
- Support for multiple admin users
- Each admin has unique credentials
- Admins can be promoted/demoted as needed

---

## Testing

### Test Admin Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@chillicare.com","password":"admin123"}'
```

Expected response:
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": "65f...",
    "email": "admin@chillicare.com",
    "user_type": "admin"
  }
}
```

### Test Admin Dashboard Access
```bash
# After login, use session cookie:
curl -X GET http://localhost:5000/api/admin/dashboard \
  -H "Cookie: session=your_session_cookie"
```

### Verify Admin in Database
```bash
python -c "
from mongodb_database import get_db
db = get_db()
admin = db.get_user_by_email('admin@chillicare.com')
print(f'Admin exists: {admin is not None}')
print(f'User type: {admin.get(\"user_type\") if admin else \"N/A\"}')
"
```

---

## Migration Steps (For Existing Systems)

If you're updating from the old system:

### Step 1: Run Admin Creation Script
```bash
python create_admin.py
```
Choose option 1, use default credentials (or custom)

### Step 2: Test Admin Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@chillicare.com","password":"admin123"}'
```

### Step 3: Remove Old Environment Variables (Optional)
You can remove these from `.env` (no longer used):
```env
# ADMIN_EMAIL=admin@chillicare.com  # Not needed anymore
# ADMIN_PASSWORD=admin123            # Not needed anymore
```

### Step 4: Update Documentation
Inform users that admin credentials are now database-stored

---

## Troubleshooting

### Issue: "No admin users found"
**Solution:** Run `python create_admin.py` to create admin user

### Issue: "Invalid credentials" when logging in as admin
**Solutions:**
1. Verify admin exists: `python create_admin.py` → option 2
2. Check password is correct (default: `admin123`)
3. Try updating password: `python create_admin.py` → option 1 → update password

### Issue: Admin not showing up as user_type='admin'
**Solution:** Check database or promote user:
```javascript
db.users.updateOne(
  { email: "admin@chillicare.com" },
  { $set: { user_type: "admin" } }
)
```

### Issue: Can't access admin dashboard
**Solutions:**
1. Verify logged in as admin: `GET /api/auth/status`
2. Check user_type is 'admin' in response
3. Ensure admin user in database has `user_type: 'admin'`

---

## API Endpoints Reference

All endpoints remain the same - admin just logs in like regular users:

### Public
- `POST /api/auth/signup` - Create farmer account
- `POST /api/auth/login` - Login (farmer or admin)
- `POST /api/auth/logout` - Logout
- `GET /api/auth/status` - Check auth status

### Admin Protected
- `GET /api/admin/dashboard` - Admin dashboard (requires user_type='admin')

### User Protected
- `GET /api/user/predictions` - User's predictions
- `GET /api/user/statistics` - User's statistics
- `DELETE /api/auth/delete-account` - Delete account (farmers only, admins cannot delete themselves)

---

## Benefits of This Change

✅ **Better Security**
   - Passwords properly hashed with bcrypt
   - No credentials in environment files
   - Same security standards as regular users

✅ **Easier Management**
   - Create/update admins via script
   - Support multiple admin users
   - Promote existing users to admin

✅ **Simpler Code**
   - No special handling for admin in load_user
   - Unified login logic for all users
   - Less complexity in authentication flow

✅ **Better Audit Trail**
   - Admin logins tracked in database
   - Last login timestamps
   - Consistent user management

✅ **Flexibility**
   - Easy to add more admins
   - Update admin passwords anytime
   - Change admin email if needed

---

## Summary

✅ Admin credentials now stored in MongoDB database  
✅ Admin user created with `python create_admin.py`  
✅ Admin login works same as regular users  
✅ Password security with bcrypt hashing  
✅ Support for multiple admin users  
✅ Easy admin management and updates  
✅ No more environment variable authentication  
✅ Cleaner, more maintainable code  

**Your admin authentication is now database-driven and production-ready!** 🎉

---

## Quick Reference

```bash
# Create admin user
python create_admin.py

# Show existing admins
python create_admin.py  # Choose option 2

# Login as admin
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@chillicare.com","password":"admin123"}'

# Check if logged in as admin
curl -X GET http://localhost:5000/api/auth/status \
  -H "Cookie: session=..."

# Access admin dashboard
curl -X GET http://localhost:5000/api/admin/dashboard \
  -H "Cookie: session=..."
```

Default admin credentials (can be changed):
- **Email:** admin@chillicare.com
- **Password:** admin123
