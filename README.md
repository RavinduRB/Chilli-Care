# Chilli Care — AI-Powered Chilli Disease Detection System

## 🌶️ Project Overview
Chilli Care is a full-stack web application for detecting diseases in chilli plants using a trained deep learning model. It provides an AI-assisted platform for farmers and agricultural professionals in Sri Lanka to identify diseases through image upload or live camera capture, with a complete user authentication system, admin dashboard, prediction history, analytics, disease reference guide, and notification system.

## 📚 Dataset
Kaggle: https://www.kaggle.com/datasets/ravindubandara3002/preprocessed-chilli-disease-dataset

## 🎯 Features

### Core Detection
- **Real-time Disease Detection** — Upload or capture chilli leaf images for instant AI diagnosis
- **Camera Capture** — Use device camera directly in the browser
- **Smart Image Validation** — Google Gemini AI verifies uploaded images are chilli plants
- **5 AI-Detectable Disease Classes** — Whitefly, Yellowish, Healthy, Anthracnose, Leaf Curl Virus
- **Confidence Scores & Probability Analysis** — Full probability breakdown for all classes
- **Prognosis Cards** — Plant life expectancy, expected yield, and next likely disease prediction

### User System
- **User Authentication** — Signup, login, logout with bcrypt-hashed passwords
- **Persistent Sessions** — 7-day login sessions via Flask-Login
- **Prediction History** — Logged-in users can view all past detections
- **Account Management** — Users can delete their own accounts

### Admin Dashboard
- **Admin Panel** — `/admin/dashboard` (admin accounts only)
- **User Management** — View all registered users
- **Prediction Analytics** — Platform-wide detection statistics and trends
- **Disease Distribution Maps** — Location-based disease spread visualisation
- **Contact Message Management** — View and reply to user contact submissions
- **Broadcast Notifications** — Send system-wide notifications to all users
- **Disease Database Editor** — Edit disease information stored in MongoDB

### Information Pages
- **Disease Reference Guide** — `/diseases` — 31 diseases & pests with symptoms, causes, prevention
- **Analytics Page** — `/analytics` — Detection statistics and charts
- **Contact Page** — `/contact` — Contact form with email notification
- **About, FAQs, Privacy, Terms** pages

## 📋 Prerequisites
- Python 3.8 or higher
- MongoDB Atlas account (or local MongoDB instance)
- Google Gemini API key (for image validation)
- Gmail account with App Password (for email notifications)

## 📁 Project Structure
```
Chilli Care/
│
├── app.py                              # Main Flask application
├── mongodb_database.py                 # MongoDB database layer
├── requirements.txt                    # Python dependencies
├── class_names.json                    # Disease class labels
│
├── best_chilli_disease_model.h5        # Primary trained model
├── chilli_disease_detection_model_final.h5
├── chilli_disease_detection_model_final.keras
├── chilli_disease_model_saved/         # TensorFlow SavedModel format
│
├── templates/
│   ├── base.html                       # Base layout
│   ├── index.html                      # Home / detection page
│   ├── diseases.html                   # Disease reference guide
│   ├── analytics.html                  # Analytics dashboard
│   ├── about.html
│   ├── contact.html
│   ├── faqs.html
│   ├── privacy.html
│   ├── terms.html
│   ├── admin_base.html
│   └── admin_dashboard.html
│
├── static/
│   ├── css/                            # Stylesheets
│   ├── js/                             # Frontend JavaScript
│   └── images/                         # Static assets
│
├── uploads/                            # Uploaded images (auto-created)
├── train/                              # Training data
├── valid/                              # Validation data
└── test/                               # Test data
```

## 🚀 Installation & Setup

### 1. Clone or Navigate to Project Directory
```bash
cd "Chilli Care"
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download BLIP Model (for Local Image Validation)
The app uses the **Salesforce BLIP** model (`Salesforce/blip-image-captioning-base`) as a local fallback for validating that uploaded images are chilli plants. The model is ~1GB and is **not included in the repository** — it is downloaded automatically from Hugging Face on first use.

**Option A — Auto-download on first run (recommended)**
Simply run the app. The model will be downloaded and cached automatically (~1GB, one-time):
```bash
python app.py
```
The model is cached at `~/.cache/huggingface/hub/` and reused on all subsequent runs.

**Option B — Pre-download before running**
Run the test script which downloads and verifies the model:
```bash
python test_huggingface_local.py
```

> **Note:** `transformers` and `torch` must be installed first (`pip install -r requirements.txt`). Without the model, the app falls back to Google Gemini API for image validation, so it will still work.

### 5. Configure Environment Variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your-strong-random-secret-key

# MongoDB
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/chillicare

# Google Gemini AI (image validation)
GEMINI_API_KEY=your_gemini_api_key_here

# Gmail (contact form & notifications)
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your_gmail_app_password
```

> **Note:** Never commit `.env` to version control. It is already listed in `.gitignore`.

### 5. Create Admin User
```bash
python add_admin_user.py
```
Or use the interactive version to set custom credentials:
```bash
python create_admin.py
```

### 6. Start the Application
```bash
python app.py
```

Access at: `http://127.0.0.1:5000`

For production with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📱 How to Use

1. **Upload or Capture** — Choose an image file or use the camera button
2. **Validation** — Gemini AI confirms the image is a chilli plant
3. **Analyze** — Click "Analyze Disease" to run the model
4. **Results** — View disease name, confidence score, symptoms, treatments, organic solutions, and prognosis
5. **History** — Log in to save and review past detections

## 🧪 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | System health check |
| `POST` | `/api/predict` | Run disease detection |
| `GET` | `/api/diseases` | List all diseases |
| `GET` | `/api/disease/<name>` | Get disease details |
| `POST` | `/api/auth/signup` | Register new user |
| `POST` | `/api/auth/login` | User login |
| `POST` | `/api/auth/logout` | User logout |
| `GET` | `/api/auth/status` | Check auth status |
| `GET` | `/api/history` | Get prediction history (auth required) |
| `GET` | `/api/user/predictions` | User's own predictions |
| `GET` | `/api/user/statistics` | User statistics |
| `GET` | `/api/analytics/summary` | Platform analytics summary |
| `POST` | `/api/contact` | Submit contact form |
| `GET` | `/api/notifications` | Get user notifications |
| `GET` | `/api/admin/dashboard` | Admin dashboard data (admin only) |
| `GET` | `/api/admin/users` | All users (admin only) |
| `GET` | `/api/admin/predictions` | All predictions (admin only) |
| `GET` | `/api/admin/messages` | Contact messages (admin only) |
| `POST` | `/api/admin/notifications/broadcast` | Broadcast notification (admin only) |

## 📊 Disease Classes (AI Detectable)

1. **Chilli Whitefly** — Insect infestation
2. **Chilli Yellowish** — Nutrient deficiency / environmental stress
3. **Chilli Healthy** — Normal healthy plant
4. **Chilli Anthracnose** — Fungal disease (*Colletotrichum* spp.)
5. **Chilli Leaf Curl Virus** — Viral disease (transmitted by whitefly)

The full disease reference guide covers 31 diseases and pests across fungal, bacterial, viral, pest, and nutritional categories.

## 🛠️ Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask, Flask-Login, Flask-Mail, Flask-CORS |
| Database | MongoDB Atlas (via PyMongo) |
| Deep Learning | TensorFlow, Keras |
| AI Validation | Google Gemini API (`google-genai`) |
| Password Security | bcrypt |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Image Processing | Pillow, NumPy |
| Deployment | Gunicorn (Procfile included) |

## 🔐 Security Notes

- Passwords are hashed with **bcrypt** (salted, never stored plain)
- Session cookies are `HttpOnly` and `SameSite=Lax`
- Set `SESSION_COOKIE_SECURE=True` and use HTTPS in production
- Set a strong `SECRET_KEY` in `.env` before deploying
- `.env` is excluded from version control via `.gitignore`

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| MongoDB not connecting | Check `MONGODB_URI` in `.env` |
| Gemini validation failing | Check `GEMINI_API_KEY` in `.env` |
| Model not loading | Ensure model `.h5` or `.keras` file is in project root |
| Port already in use | Change port in `app.py` or kill the process |
| Email not sending | Check Gmail App Password and `MAIL_USERNAME` in `.env` |

## 📄 License
Final year project — for educational purposes.

## 🎓 Credits
Chilli Care — AI-Powered Chilli Disease Detection System
Powered by TensorFlow, Flask, MongoDB, and Google Gemini AI
