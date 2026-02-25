# MongoDB Setup Guide for Chilli Disease Detection System

## 🎯 Overview

This guide will help you set up MongoDB (NoSQL database) for your Chilli Care application. MongoDB provides:

- ✅ **Flexible Schema** - Perfect for your JSON-like disease data
- ✅ **Free Tier** - MongoDB Atlas offers 512MB free storage
- ✅ **Fast Queries** - Optimized for document retrieval
- ✅ **Easy Scaling** - Grows with your application
- ✅ **Cloud Hosting** - No server setup needed

---

## 📋 What You Get

### Collections:
1. **diseases** - Stores all disease information (symptoms, treatments, etc.)
2. **predictions** - Tracks every disease detection with confidence scores

### New API Endpoints:
- `GET /api/history` - View prediction history (paginated)
- `GET /api/analytics/summary` - Get overall statistics
- `GET /api/analytics/daily` - Daily prediction trends

---

## 🚀 Step-by-Step Setup

### Step 1: Create MongoDB Atlas Account

1. Go to [https://www.mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Click **"Try Free"** or **"Sign Up"**
3. Sign up with:
   - Google
   - GitHub
   - Or email address
4. Verify your email if required

### Step 2: Create a New Cluster

1. After login, click **"Build a Database"** or **"Create"**
2. Choose **"M0 FREE"** tier
   - **Provider**: AWS, Google Cloud, or Azure (any works)
   - **Region**: Choose closest to your location
   - **Cluster Name**: `chilli-care` (or any name you like)
3. Click **"Create"** (takes 1-3 minutes)

### Step 3: Create Database User

1. You'll see **"Security Quickstart"**
2. Create a database user:
   - **Username**: `chilli_admin` (or your choice)
   - **Password**: Click **"Autogenerate Secure Password"** or create your own
   - **⚠️ IMPORTANT**: Copy and save the password! You won't see it again
3. Click **"Create User"**

### Step 4: Set Network Access

1. Still in Security Quickstart, add IP address:
   - **For development**: Click **"Add My Current IP Address"**
   - **For production**: Use **"0.0.0.0/0"** (allow from anywhere)
   - ⚠️ Note: `0.0.0.0/0` is less secure but needed for deployed apps
2. Click **"Finish and Close"**

### Step 5: Get Your Connection String

1. Click **"Connect"** on your cluster
2. Choose **"Connect your application"**
3. Select:
   - **Driver**: Python
   - **Version**: 3.12 or later
4. Copy the connection string (looks like this):
   ```
   mongodb+srv://chilli_admin:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. **Replace `<password>`** with your actual password
6. **Add database name** before the `?`:
   ```
   mongodb+srv://chilli_admin:yourpassword@cluster0.xxxxx.mongodb.net/chilli_care?retryWrites=true&w=majority
   ```

### Step 6: Configure Environment Variables

1. Open your `.env` file (or create one if it doesn't exist)
2. Add your MongoDB connection string:

```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://chilli_admin:yourpassword@cluster0.xxxxx.mongodb.net/chilli_care?retryWrites=true&w=majority

# Existing API Keys (keep these)
GEMINI_API_KEY=your-gemini-key
# ... other keys
```

**Important Security Notes**:
- Replace `yourpassword` with your actual password
- Never commit `.env` file to Git (it's already in `.gitignore`)
- Keep your connection string private

### Step 7: Initialize the Database

Run the initialization script to create collections and populate disease data:

#### On Windows (Git Bash):
```bash
source .venv/Scripts/activate
python init_mongodb.py
```

#### On Windows (Command Prompt):
```cmd
.venv\Scripts\activate
python init_mongodb.py
```

#### On Linux/Mac:
```bash
source .venv/bin/activate
python init_mongodb.py
```

You should see:
```
✅ Connected to MongoDB successfully!
✅ Successfully added 5 diseases to database!
✅ MongoDB initialization complete!
```

### Step 8: Verify Installation

1. Start your Flask app:
   ```bash
   python app.py
   ```

2. Test the health endpoint:
   ```bash
   curl http://localhost:5000/api/health
   ```

3. You should see:
   ```json
   {
     "status": "healthy",
     "mongodb": "connected",
     ...
   }
   ```

---

## 📊 Using MongoDB

### View Prediction History

```bash
# Get last 20 predictions
curl http://localhost:5000/api/history

# Filter by disease
curl "http://localhost:5000/api/history?disease=Chilli%20Whitefly"

# Pagination
curl "http://localhost:5000/api/history?page=2&per_page=50"
```

### Get Analytics

```bash
# Overall summary
curl http://localhost:5000/api/analytics/summary

# Daily trends (last 30 days)
curl http://localhost:5000/api/analytics/daily

# Custom date range
curl "http://localhost:5000/api/analytics/daily?days=90"
```

---

## 🗂️ MongoDB Data Structure

### Diseases Collection
```javascript
{
  "_id": ObjectId("..."),
  "name": "Chilli Whitefly",
  "severity": "Medium",
  "description": "...",
  "symptoms": ["...", "..."],
  "causes": ["...", "..."],
  "treatment": ["...", "..."],
  "prevention": ["...", "..."],
  "organic_solutions": ["...", "..."],
  "created_at": ISODate("2026-02-25T..."),
  "updated_at": ISODate("2026-02-25T...")
}
```

### Predictions Collection
```javascript
{
  "_id": ObjectId("..."),
  "image_filename": "leaf_image.jpg",
  "predicted_disease": "Chilli Whitefly",
  "confidence": 95.67,
  "all_probabilities": {
    "Chilli Whitefly": 95.67,
    "Chilli healthy": 2.31,
    ...
  },
  "top_3_predictions": [
    ["Chilli Whitefly", 95.67],
    ["Chilli healthy", 2.31],
    ...
  ],
  "validation_method": "Gemini API",
  "validation_message": "Image validated...",
  "user_ip": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "model_version": "1.0.0",
  "timestamp": ISODate("2026-02-25T...")
}
```

---

## 🔍 Viewing Data in MongoDB Atlas

### Using Atlas Web Interface:

1. Go to [https://cloud.mongodb.com](https://cloud.mongodb.com)
2. Click **"Browse Collections"** on your cluster
3. Select `chilli_care` database
4. Browse **diseases** and **predictions** collections
5. Use filters and queries to explore data

### Example Queries:

**Find all Whitefly predictions:**
```javascript
{ "predicted_disease": "Chilli Whitefly" }
```

**Find high-confidence predictions:**
```javascript
{ "confidence": { "$gt": 90 } }
```

**Find recent predictions:**
```javascript
{ "timestamp": { "$gte": new Date("2026-02-24") } }
```

---

## 🛠️ Maintenance & Management

### View Database Stats

```python
from mongodb_database import get_db

# Get database instance
db = get_db()

# Check connection
print(f"Connected: {db.connected}")

# View collections
print(f"Collections: {db.db.list_collection_names()}")

# Count documents
print(f"Diseases: {db.db.diseases.count_documents({})}")
print(f"Predictions: {db.db.predictions.count_documents({})}")
```

### Backup Data

MongoDB Atlas provides automatic backups on paid tiers. For free tier:

1. **Manual Export**:
   - Go to Atlas Dashboard
   - Click "Collections"
   - Click "..." menu → "Export Collection"
   - Download as JSON

2. **Using Python**:
```python
from mongodb_database import get_db
import json

db = get_db()

# Export all predictions
predictions = db.get_predictions(limit=10000)
with open('predictions_backup.json', 'w') as f:
    json.dump(predictions, f, default=str)
```

### Reset Database

⚠️ **WARNING**: This deletes all data!

```bash
python init_mongodb.py
# Answer 'yes' when prompted
```

---

## 📈 Monitoring & Limits

### MongoDB Atlas Free Tier Limits:
- **Storage**: 512MB
- **RAM**: Shared
- **Connections**: 500 concurrent
- **Data Transfer**: No limit on free tier

### Check Usage:
1. Go to Atlas Dashboard
2. Select your cluster
3. Click **"Metrics"** tab
4. View storage, connections, operations

### When to Upgrade:
- ✅ Approaching 512MB storage
- ✅ Need automated backups
- ✅ Need better performance
- ✅ Need dedicated resources

**Upgrade Options**: M2 ($9/month) or M10 ($57/month)

---

## ❌ Troubleshooting

### Error: "MONGODB_URI not found"
**Solution**: Add `MONGODB_URI` to your `.env` file

### Error: "Authentication failed"
**Solutions**:
1. Check username and password in connection string
2. Verify user exists in Atlas → Database Access
3. Try resetting password

### Error: "Connection timeout"
**Solutions**:
1. Check network/firewall
2. Add your IP to Atlas → Network Access
3. Use `0.0.0.0/0` for testing (not recommended for production)

### Error: "Server selection timeout"
**Solutions**:
1. Verify connection string is correct
2. Check if cluster is active (not paused)
3. Ensure `dnspython` is installed: `pip install dnspython`

### Database not updating
**Solutions**:
1. Check connection: `curl http://localhost:5000/api/health`
2. View app logs for errors
3. Verify `MONGODB_URI` is correct
4. Test connection in Atlas web interface

### Collections don't exist
**Solution**: Run initialization script again:
```bash
python init_mongodb.py
```

---

## 🔐 Security Best Practices

1. **Never expose connection string**
   - Don't commit `.env` to Git
   - Use environment variables in production
   
2. **Use strong passwords**
   - Auto-generate in Atlas
   - Or use 20+ characters with symbols

3. **Limit IP access**
   - Use specific IPs when possible
   - `0.0.0.0/0` only for deployed apps

4. **Create separate users**
   - Read-only user for analytics
   - Admin user for updates
   - App user with limited permissions

5 **Enable connection encryption**
   - Already enabled with `mongodb+srv://`
   - Always use SRV format

---

## 🎓 Next Steps

### Optional Enhancements:

1. **Add Indexes**
   ```python
   db.db.predictions.create_index([("predicted_disease", 1), ("timestamp", -1)])
   ```

2. **Implement Caching**
   - Cache frequently accessed diseases
   - Use Redis or in-memory caching

3. **Add Data Validation**
   - MongoDB schema validation
   - Pydantic models for data integrity

4. **Set up Monitoring**
   - MongoDB Atlas alerts
   - Application performance monitoring

5. **Advanced Analytics**
   - Aggregation pipelines
   - Time-series analysis
   - Geographic distribution

---

## 📞 Support & Resources

- **MongoDB Documentation**: [https://docs.mongodb.com](https://docs.mongodb.com)
- **PyMongo Guide**: [https://pymongo.readthedocs.io](https://pymongo.readthedocs.io)
- **Atlas Support**: [https://support.mongodb.com](https://support.mongodb.com)
- **Community Forums**: [https://community.mongodb.com](https://community.mongodb.com)

---

## ✅ Quick Reference

### Essential Commands:
```bash
# Activate environment
source .venv/Scripts/activate  # Windows Git Bash
.venv\Scripts\activate         # Windows CMD

# Initialize database
python init_mongodb.py

# Start application
python app.py

# Test connection
curl http://localhost:5000/api/health
```

### Key Files:
- `mongodb_database.py` - MongoDB connection and operations
- `init_mongodb.py` - Database initialization script
- `app.py` - Flask app with MongoDB integration
- `.env` - Environment variables (MONGODB_URI)
- `MONGODB_SETUP.md` - This guide

---

🎉 **Congratulations!** Your Chilli Care system is now powered by MongoDB with full analytics capabilities!
