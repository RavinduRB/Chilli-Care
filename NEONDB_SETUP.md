# NeonDB Setup Guide for Chilli Disease Detection System

## 🎯 Overview

This guide will help you set up NeonDB (Serverless PostgreSQL) for your Chilli Care application. NeonDB provides:

- ✅ **Free Tier**: 512MB storage, perfect for getting started
- ✅ **Serverless**: Auto-scales, pay only for what you use
- ✅ **JSONB Support**: Store complex disease information efficiently
- ✅ **Easy Integration**: Works seamlessly with Flask-SQLAlchemy
- ✅ **Analytics**: Track prediction history and generate insights

---

## 📋 What You Get

### Database Tables:
1. **diseases** - Stores all disease information (symptoms, treatments, etc.)
2. **predictions** - Tracks every disease detection with confidence scores
3. **daily_stats** - Aggregated analytics for dashboard

### New API Endpoints:
- `GET /api/history` - View prediction history (paginated)
- `GET /api/analytics/summary` - Get overall statistics
- `GET /api/analytics/daily` - Daily prediction trends

---

## 🚀 Step-by-Step Setup

### Step 1: Create NeonDB Account

1. Go to [https://neon.tech](https://neon.tech)
2. Click **"Sign Up"** (free account)
3. Sign up with GitHub, Google, or email
4. Verify your email if required

### Step 2: Create a New Project

1. In NeonDB dashboard, click **"New Project"**
2. Fill in:
   - **Project Name**: `chilli-care` (or your preferred name)
   - **PostgreSQL Version**: `16` (latest recommended)
   - **Region**: Choose closest to your location
3. Click **"Create Project"**

### Step 3: Get Your Connection String

1. After project creation, you'll see **"Connection Details"**
2. Click **"Connection string"** tab
3. Copy the connection string (looks like this):
   ```
   postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
   ```
4. Keep this safe! You'll need it next.

### Step 4: Configure Environment Variables

1. Open your `.env` file (or create one if it doesn't exist)
2. Add your NeonDB connection string:

```env
# NeonDB Configuration
DATABASE_URL=postgresql://your-username:your-password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require

# Existing API Keys (keep these)
GEMINI_API_KEY=your-gemini-key
GEMINI_API_KEY_2=your-second-key
# ... other keys
```

**Important**: Replace the entire `DATABASE_URL` value with your actual connection string from NeonDB.

### Step 5: Initialize the Database

Run the initialization script to create tables and populate disease data:

#### On Windows (Git Bash):
```bash
source .venv/Scripts/activate
python init_database.py
```

#### On Windows (Command Prompt):
```cmd
.venv\Scripts\activate
python init_database.py
```

#### On Linux/Mac:
```bash
source .venv/bin/activate
python init_database.py
```

You should see:
```
✅ Tables created successfully!
✅ Successfully added 5 diseases to database!
✅ Database initialization complete!
```

### Step 6: Verify Installation

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
     "database": "connected",
     ...
   }
   ```

---

## 📊 Using the Database

### View Prediction History

```bash
# Get last 20 predictions
curl http://localhost:5000/api/history

# Filter by disease
curl http://localhost:5000/api/history?disease=Chilli%20Whitefly

# Pagination
curl http://localhost:5000/api/history?page=2&per_page=50
```

### Get Analytics

```bash
# Overall summary
curl http://localhost:5000/api/analytics/summary

# Daily trends (last 30 days)
curl http://localhost:5000/api/analytics/daily

# Custom date range
curl http://localhost:5000/api/analytics/daily?days=90
```

---

## 🔍 Database Schema

### Diseases Table
```sql
CREATE TABLE diseases (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    symptoms JSONB NOT NULL,
    causes JSONB NOT NULL,
    treatment JSONB NOT NULL,
    prevention JSONB NOT NULL,
    organic_solutions JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Predictions Table
```sql
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    image_filename VARCHAR(255),
    predicted_disease VARCHAR(100) NOT NULL,
    disease_id INTEGER REFERENCES diseases(id),
    confidence FLOAT NOT NULL,
    all_probabilities JSONB NOT NULL,
    top_3_predictions JSONB NOT NULL,
    validation_method VARCHAR(100),
    validation_message TEXT,
    user_ip VARCHAR(45),
    user_agent VARCHAR(500),
    timestamp TIMESTAMP DEFAULT NOW(),
    model_version VARCHAR(20) DEFAULT '1.0.0'
);
```

---

## 🛠️ Maintenance Tasks

### View All Predictions
```python
from app import app, db, Prediction

with app.app_context():
    predictions = Prediction.query.order_by(Prediction.timestamp.desc()).limit(10).all()
    for p in predictions:
        print(f"{p.timestamp}: {p.predicted_disease} ({p.confidence:.2f}%)")
```

### Get Disease Statistics
```python
from app import app, db, Disease, Prediction
from sqlalchemy import func

with app.app_context():
    stats = db.session.query(
        Prediction.predicted_disease,
        func.count(Prediction.id),
        func.avg(Prediction.confidence)
    ).group_by(Prediction.predicted_disease).all()
    
    for disease, count, avg_conf in stats:
        print(f"{disease}: {count} predictions (avg confidence: {avg_conf:.2f}%)")
```

### Reset Database (USE WITH CAUTION!)
```bash
python init_database.py
# Answer 'yes' when prompted to recreate data
```

---

## 🔐 Security Best Practices

1. **Never commit `.env` file** to Git
   - Already in `.gitignore` ✅
   - Contains sensitive database credentials

2. **Use different databases for dev/prod**
   - Create separate NeonDB projects
   - Use different `DATABASE_URL` for each environment

3. **Rotate credentials periodically**
   - NeonDB Dashboard → Settings → Reset Password

4. **Enable connection pooling** (already configured)
   - Handles multiple concurrent requests efficiently

---

## 📈 Monitoring & Limits

### NeonDB Free Tier Limits:
- **Storage**: 512MB
- **Compute**: 191.9 compute hours/month
- **Data Transfer**: Shared (fair use)

### Check Usage:
1. Go to NeonDB Dashboard
2. Select your project
3. View **"Usage"** tab

### When to Upgrade:
- Approaching 512MB storage
- Need more compute hours
- Want automatic backups
- Require point-in-time restore

---

## ❌ Troubleshooting

### Error: "No DATABASE_URL found"
**Solution**: Add `DATABASE_URL` to your `.env` file

### Error: "Connection refused"
**Solutions**:
1. Check connection string is correct
2. Ensure `?sslmode=require` is in URL
3. Verify NeonDB project is active (not paused)

### Error: "psycopg2 not installed"
**Solution**:
```bash
pip install psycopg2-binary
```

### Database not updating
**Solutions**:
1. Check database connection: `curl http://localhost:5000/api/health`
2. View logs in terminal for errors
3. Verify `DATABASE_URL` is set correctly

### Tables don't exist
**Solution**: Run initialization script again:
```bash
python init_database.py
```

---

## 🎓 Next Steps

### Optional Enhancements:

1. **Add User Authentication**
   - Install Flask-Login
   - Track predictions per user
   - User dashboard

2. **Image Storage**
   - Store uploaded images in database or S3
   - Link predictions to actual images

3. **Email Notifications**
   - Alert users of high-severity diseases
   - Weekly analytics emails

4. **Export Reports**
   - CSV export of prediction history
   - PDF treatment recommendations

5. **Advanced Analytics**
   - Disease outbreak detection
   - Seasonal trend analysis
   - Geographic distribution (if location data added)

---

## 📞 Support

- **NeonDB Docs**: [https://neon.tech/docs](https://neon.tech/docs)
- **Flask-SQLAlchemy**: [https://flask-sqlalchemy.palletsprojects.com](https://flask-sqlalchemy.palletsprojects.com)
- **PostgreSQL JSONB**: [https://www.postgresql.org/docs/current/datatype-json.html](https://www.postgresql.org/docs/current/datatype-json.html)

---

## ✅ Quick Reference

### Essential Commands:
```bash
# Activate environment
source .venv/Scripts/activate  # Windows Git Bash
.venv\Scripts\activate         # Windows CMD

# Initialize database
python init_database.py

# Start application
python app.py

# Test database connection
curl http://localhost:5000/api/health
```

### Key Files:
- `models.py` - Database models (diseases, predictions, stats)
- `init_database.py` - Database setup script
- `app.py` - Main application with database integration
- `.env` - Environment variables (DATABASE_URL)
- `NEONDB_SETUP.md` - This guide

---

🎉 **Congratulations!** Your Chilli Care system is now powered by NeonDB with full analytics capabilities!
