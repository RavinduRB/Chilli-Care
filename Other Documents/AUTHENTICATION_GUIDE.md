# Authentication System Guide

## Overview
The Chilli Care application now includes a complete user authentication system with two types of users: **Farmers** and **Admins**.

## User Types

### 1. Farmers
- Regular users who want to use the disease detection system
- Must register with email and password
- Data stored in MongoDB
- Each farmer has their own profile
- Can delete their account at any time

### 2. Admins
- System administrators with special access
- All admins share the same credentials
- Not stored in MongoDB (configured via environment variables)
- Cannot delete admin accounts

## Features

### For All Users
- **Login/Signup**: Clean modal-based authentication UI
- **Profile Dropdown**: Access to logout and account management
- **Protected Analysis**: Only authenticated users can analyze plant images
- **Session Management**: Automatic session handling with Flask-Login

### Authentication Flow
1. **New Users**: Click "Sign Up" → Enter email & password → Account created automatically
2. **Existing Users**: Click "Log In" → Enter credentials → Access granted
3. **Non-authenticated users**: Attempting to analyze images shows login prompt

## Configuration

### Admin Credentials
Set these environment variables in your `.env` file:

```env
ADMIN_EMAIL=admin@chillicare.com
ADMIN_PASSWORD=your_secure_password
```

**Default credentials (if not set):**
- Email: `admin@chillicare.com`
- Password: `admin123`

⚠️ **Important**: Change the default admin password in production!

### Secret Key
Set a secure secret key for session management:

```env
SECRET_KEY=your_very_secure_random_secret_key
```

## Database Schema

### Users Collection
```javascript
{
  "_id": ObjectId,
  "email": String (unique, indexed),
  "password": String (bcrypt hashed),
  "user_type": String ("farmer" or "admin"),
  "created_at": DateTime,
  "last_login": DateTime
}
```

## API Endpoints

### Authentication Routes
- `POST /api/auth/signup` - Create new farmer account
- `POST /api/auth/login` - Login (farmers or admin)
- `POST /api/auth/logout` - Logout current user
- `DELETE /api/auth/delete-account` - Delete farmer account (protected)
- `GET /api/auth/status` - Check authentication status

### Protected Routes
- `POST /api/predict` - Disease prediction (requires login)

## Frontend Components

### Navbar Authentication Section
- Shows login/signup buttons when not authenticated
- Shows profile icon with user email when authenticated
- Profile dropdown with logout and delete account options

### Modals
- **Login Modal**: Email and password fields
- **Signup Modal**: Email, password, and confirm password fields
- Form validation and error messages
- Easy switching between login and signup

## Security Features

1. **Password Hashing**: Bcrypt with salt for farmer passwords
2. **Session Management**: Flask-Login for secure sessions
3. **Input Validation**: Email format and password length checks
4. **SQL Injection Prevention**: MongoDB with parameterized queries
5. **XSS Prevention**: Proper input sanitization
6. **CSRF Protection**: Flask built-in CSRF tokens (via Flask-Login)

## Testing the System

### Test as Farmer
1. Open the application
2. Click "Sign Up" button
3. Enter email: `farmer@test.com`
4. Enter password: `password123`
5. Create account and test disease detection

### Test as Admin
1. Click "Log In" button
2. Enter email: `admin@chillicare.com`
3. Enter default password: `admin123`
4. Access granted with admin privileges

## Troubleshooting

### "Database not available" error
- Check MongoDB connection string in `.env`
- Ensure MongoDB is running
- Check network connectivity

### Cannot login
- Verify email format is correct
- Check password meets minimum length (6 characters)
- For admin: verify environment variables are set correctly

### Session expires quickly
- Check if SECRET_KEY is properly set
- Ensure cookies are enabled in browser

## Future Enhancements
- Email verification for new accounts
- Password reset functionality
- Two-factor authentication
- User roles and permissions
- Activity logging and audit trails
