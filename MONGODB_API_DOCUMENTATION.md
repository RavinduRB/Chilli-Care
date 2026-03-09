# MongoDB Database & API Documentation

## Overview
Your Chilli Disease Detection system now fully integrates with MongoDB to store and manage:
- **User Authentication** - User accounts, login sessions, and credentials
- **Disease Information** - Detailed disease data with symptoms, treatments, and prevention
- **Predictions** - Complete prediction history with user tracking and analytics

---

## Database Collections

### 1. Users Collection (`users`)
Stores all registered user accounts.

**Schema:**
```json
{
  "_id": "ObjectId",
  "email": "user@example.com",
  "password": "hashed_password_with_bcrypt",
  "user_type": "farmer|admin",
  "created_at": "2026-03-09T...",
  "last_login": "2026-03-09T..."
}
```

**Indexes:**
- `email` (unique)
- `user_type`

---

### 2. Diseases Collection (`diseases`)
Contains all chilli disease information.

**Schema:**
```json
{
  "_id": "ObjectId",
  "name": "Chilli Leaf Curl Virus",
  "severity": "Very High",
  "description": "Description of the disease...",
  "symptoms": ["symptom1", "symptom2"],
  "causes": ["cause1", "cause2"],
  "treatment": ["treatment1", "treatment2"],
  "prevention": ["prevention1", "prevention2"],
  "organic_solutions": ["solution1", "solution2"],
  "created_at": "2026-03-09T...",
  "updated_at": "2026-03-09T..."
}
```

**Indexes:**
- `name` (unique)

**Current Diseases:**
- Chilli Whitefly (Medium severity)
- Chilli Yellowish (High severity)
- Chilli healthy (None)
- Chilli Anthacnose (High severity)
- Chilli Leaf Curl Virus (Very High severity)

---

### 3. Predictions Collection (`predictions`)
Stores all prediction history with user tracking.

**Schema:**
```json
{
  "_id": "ObjectId",
  "image_filename": "plant_image.jpg",
  "predicted_disease": "Chilli Leaf Curl Virus",
  "confidence": 0.95,
  "all_probabilities": {...},
  "top_3_predictions": [["disease", 0.95], ...],
  "validation_method": "gemini-flash",
  "validation_message": "Confirmed chilli plant...",
  "user_id": "user_object_id",
  "user_email": "user@example.com",
  "user_type": "farmer",
  "user_ip": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "model_version": "1.0.0",
  "timestamp": "2026-03-09T..."
}
```

**Indexes:**
- `timestamp` (descending)
- `predicted_disease`
- `confidence` (descending)

---

## Authentication API Endpoints

### 1. User Signup
**POST** `/api/auth/signup`

**Request Body:**
```json
{
  "email": "farmer@example.com",
  "password": "secure_password"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Account created successfully",
  "user": {
    "email": "farmer@example.com",
    "user_type": "farmer"
  }
}
```

**Errors:**
- 400: Invalid email format or password too short
- 409: Email already registered
- 500: Database error

---

### 2. User Login
**POST** `/api/auth/login`

**Request Body:**
```json
{
  "email": "farmer@example.com",
  "password": "secure_password"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "email": "farmer@example.com",
    "user_type": "farmer"
  }
}
```

**Admin Login:**
```json
{
  "email": "admin@chillicare.com",
  "password": "admin123"
}
```

**Errors:**
- 400: Missing credentials
- 401: Invalid credentials
- 500: Database error

---

### 3. User Logout
**POST** `/api/auth/logout`

**Requires:** Authentication

**Response (200):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

### 4. Delete Account
**DELETE** `/api/auth/delete-account`

**Requires:** Authentication (farmers only, not admins)

**Response (200):**
```json
{
  "success": true,
  "message": "Account deleted successfully"
}
```

---

## Disease API Endpoints

### 1. Get All Diseases
**GET** `/api/diseases`

**Response:**
```json
{
  "success": true,
  "diseases": {
    "Chilli Whitefly": {
      "severity": "Medium",
      "description": "...",
      "symptoms": [...],
      "causes": [...],
      "treatment": [...],
      "prevention": [...],
      "organic_solutions": [...]
    },
    ...
  },
  "total_diseases": 5,
  "source": "mongodb"
}
```

---

### 2. Get Specific Disease
**GET** `/api/disease/<disease_name>`

**Example:** `/api/disease/Chilli%20Leaf%20Curl%20Virus`

**Response:**
```json
{
  "success": true,
  "disease_name": "Chilli Leaf Curl Virus",
  "info": {
    "severity": "Very High",
    "description": "...",
    ...
  }
}
```

---

## Prediction API Endpoints

### 1. Make Prediction
**POST** `/api/predict`

**Request:** Multipart form-data with 'file' field

**Response:**
```json
{
  "success": true,
  "prediction": {
    "predicted_class": "Chilli Leaf Curl Virus",
    "confidence": 0.95,
    "all_probabilities": {...},
    "top_3_predictions": [...]
  },
  "disease_info": {...},
  "timestamp": "2026-03-09T...",
  "model_version": "1.0.0",
  "prediction_id": "65f..."
}
```

**Note:** Automatically saves to database with user information if logged in.

---

### 2. Get Prediction History (All)
**GET** `/api/history`

**Query Parameters:**
- `page` (default: 1)
- `per_page` (default: 20)
- `disease` (optional filter)

**Example:** `/api/history?page=1&per_page=10&disease=Chilli%20Whitefly`

**Response:**
```json
{
  "success": true,
  "predictions": [...],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "total_pages": 5
}
```

---

### 3. Get User's Predictions
**GET** `/api/user/predictions`

**Requires:** Authentication

**Query Parameters:**
- `page` (default: 1)
- `per_page` (default: 20)

**Response:**
```json
{
  "success": true,
  "predictions": [...],
  "total": 25,
  "page": 1,
  "per_page": 20,
  "total_pages": 2
}
```

---

### 4. Get User Statistics
**GET** `/api/user/statistics`

**Requires:** Authentication

**Response:**
```json
{
  "success": true,
  "total_predictions": 25,
  "disease_stats": [
    {
      "disease": "Chilli Leaf Curl Virus",
      "count": 10,
      "avg_confidence": 0.92,
      "max_confidence": 0.98,
      "min_confidence": 0.85,
      "last_prediction": "2026-03-09T..."
    },
    ...
  ],
  "user": {
    "email": "farmer@example.com",
    "user_type": "farmer"
  }
}
```

---

## Admin API Endpoints

### 1. Admin Dashboard
**GET** `/api/admin/dashboard`

**Requires:** Admin authentication

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_users": 150,
    "total_farmers": 148,
    "total_predictions": 5000,
    "recent_predictions_7d": 250
  },
  "disease_stats": [
    {
      "disease": "Chilli Leaf Curl Virus",
      "count": 1200,
      "avg_confidence": 0.89,
      "max_confidence": 0.99,
      "min_confidence": 0.45
    },
    ...
  ],
  "recent_users": [
    {
      "_id": "65f...",
      "email": "user@example.com",
      "user_type": "farmer",
      "created_at": "2026-03-09T...",
      "last_login": "2026-03-09T..."
    },
    ...
  ]
}
```

---

## Analytics API Endpoints

### 1. Disease Statistics
**GET** `/api/analytics`

**Response:**
```json
{
  "success": true,
  "statistics": [
    {
      "disease": "Chilli Leaf Curl Virus",
      "count": 1200,
      "avg_confidence": 0.89,
      "percentage": 24.5
    },
    ...
  ],
  "total_predictions": 5000,
  "recent_predictions": 250
}
```

---

### 2. Daily Analytics
**GET** `/api/analytics/daily`

**Query Parameters:**
- `days` (default: 30)

**Example:** `/api/analytics/daily?days=7`

**Response:**
```json
{
  "success": true,
  "daily_stats": [
    {
      "date": "2026-03-09",
      "count": 45
    },
    {
      "date": "2026-03-08",
      "count": 38
    },
    ...
  ]
}
```

---

## MongoDB Database Operations

### User Operations (mongodb_database.py)

```python
# Create user
user_id = mongodb.create_user(email, password_hash, user_type='farmer')

# Get user by email
user = mongodb.get_user_by_email(email)

# Get user by ID
user = mongodb.get_user_by_id(user_id)

# Update last login
mongodb.update_last_login(email)

# Delete user
mongodb.delete_user(email)

# Count users
total = mongodb.count_users(user_type='farmer')

# Get all users
users = mongodb.get_all_users(skip=0, limit=50)
```

---

### Disease Operations

```python
# Get disease by name
disease = mongodb.get_disease(disease_name)

# Get all diseases
diseases = mongodb.get_all_diseases()

# Insert/update disease
disease_id = mongodb.insert_disease(disease_data)
```

---

### Prediction Operations

```python
# Save prediction
prediction_id = mongodb.save_prediction(prediction_data)

# Get predictions with pagination
predictions = mongodb.get_predictions(limit=20, skip=0, disease_filter='Chilli Whitefly')

# Count predictions
total = mongodb.count_predictions(disease_filter='Chilli Whitefly')

# Get user's predictions
predictions = mongodb.get_user_predictions(user_id, limit=20, skip=0)

# Count user's predictions
total = mongodb.count_user_predictions(user_id)

# Get user disease statistics
stats = mongodb.get_user_disease_statistics(user_id)
```

---

### Analytics Operations

```python
# Get disease statistics
stats = mongodb.get_disease_statistics()

# Get daily statistics
daily_stats = mongodb.get_daily_statistics(days=30)

# Get recent predictions count
recent = mongodb.get_recent_predictions_count(days=7)
```

---

## Environment Variables Required

Add to your `.env` file:

```env
# MongoDB Connection
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database_name

# Admin Credentials
ADMIN_EMAIL=admin@chillicare.com
ADMIN_PASSWORD=admin123

# Flask Secret Key
SECRET_KEY=your-secret-key-here-change-in-production
```

---

## Initialization

### Initialize Database with Diseases

```bash
python init_mongodb.py
```

This will:
1. Connect to MongoDB
2. Clear existing disease data (if confirmed)
3. Populate all 5 diseases
4. Display summary

---

## Testing the API

### 1. Test User Signup
```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### 2. Test User Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### 3. Test Admin Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@chillicare.com","password":"admin123"}'
```

### 4. Get All Diseases
```bash
curl http://localhost:5000/api/diseases
```

### 5. Make Prediction
```bash
curl -X POST http://localhost:5000/api/predict \
  -F "file=@path/to/chilli_leaf.jpg"
```

---

## Database Security

### Password Hashing
- All user passwords are hashed using **bcrypt** with salt
- Passwords are never stored in plain text
- Password minimum length: 6 characters

### Admin Access
- Admin credentials stored in environment variables
- Admin accounts not stored in database
- Admin-only endpoints protected with `@login_required` and user_type check

### Session Management
- Sessions managed by Flask-Login
- Persistent sessions (7 days)
- Secure cookies (HTTP-only)

---

## Common Issues & Solutions

### Issue: "Database not available"
**Solution:** Check MONGODB_URI in .env file and network connection

### Issue: "Email already registered"
**Solution:** Use different email or delete existing user

### Issue: "Invalid credentials"
**Solution:** Check email and password are correct

### Issue: "Unauthorized - Admin access required"
**Solution:** Login with admin credentials for admin endpoints

---

## Summary

✅ **User Authentication** - Fully functional signup, login, logout, and account deletion  
✅ **Disease Database** - All 5 diseases populated with complete information  
✅ **Predictions Tracking** - All predictions saved with user information  
✅ **User Analytics** - Personal prediction history and statistics  
✅ **Admin Dashboard** - Comprehensive system analytics  
✅ **Security** - Bcrypt password hashing, session management  

Your system is now production-ready with full MongoDB integration!
