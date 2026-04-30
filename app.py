"""
Chilli Disease Detection - Industry-Level Web Application
Modern Flask API with TensorFlow Model Integration
"""

import os
import json
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import tensorflow as tf
from tensorflow import keras
from PIL import Image
import io
import base64
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv
import requests
import bcrypt
from functools import lru_cache

# Load environment variables from .env file
load_dotenv()

# Location cache to avoid repeated API calls
location_cache = {}

# Import Hugging Face Transformers for local BLIP model
try:
    from transformers import BlipProcessor, BlipForConditionalGeneration
    import torch
    TRANSFORMERS_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✓ Transformers library loaded successfully")
except ImportError as e:
    TRANSFORMERS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠ Transformers not available: {e}")

# Configure logging (must be before MongoDB import that uses logger)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import MongoDB database
mongodb = None
try:
    from mongodb_database import get_db
    mongodb = get_db()
    if mongodb and mongodb.connected:
        logger.info(f"✓ MongoDB connected successfully")
    else:
        logger.warning("⚠ MongoDB not connected - check MONGODB_URI in .env")
        mongodb = None
except ImportError as e:
    logger.warning(f"⚠ MongoDB import failed: {e}")
    mongodb = None
except Exception as e:
    logger.error(f"❌ MongoDB connection error: {e}")
    mongodb = None

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Session configuration for persistent login
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Session lasts 7 days
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Email configuration for Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Your Gmail address
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Your Gmail App Password
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME', 'noreply@chillicare.com')

CORS(app)  # Enable CORS for API access

# Initialize Flask-Mail
mail = Mail(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'  # Redirect to index if not logged in

@login_manager.unauthorized_handler
def unauthorized():
    """Handle unauthorized access"""
    # For API endpoints, return JSON
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    # For page routes, redirect to home
    return redirect('/')

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id, email, user_type):
        self.id = user_id
        self.email = email
        self.user_type = user_type
    
    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    try:
        # Load all users from database (including admin)
        if mongodb and mongodb.connected:
            user_data = mongodb.get_user_by_id(user_id)
            if user_data:
                return User(str(user_data['_id']), user_data['email'], user_data['user_type'])
        else:
            logger.warning("MongoDB not connected in load_user")
    except Exception as e:
        logger.error(f"Error loading user: {e}")
    return None

# Configure Multiple Gemini API Keys for Rotation
GEMINI_API_KEYS = [
    os.environ.get('GEMINI_API_KEY', ''),
    os.environ.get('GEMINI_API_KEY_2', ''),
]
# Remove empty keys
GEMINI_API_KEYS = [key for key in GEMINI_API_KEYS if key]

# Hugging Face - No API key needed for local model
HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY', '')  # Deprecated - using local model now

if GEMINI_API_KEYS:
    logger.info(f"✓ Configured {len(GEMINI_API_KEYS)} Gemini API key(s)")
else:
    logger.warning("⚠ No Gemini API keys set")

# Note: Local BLIP model will be loaded on first use
logger.info("✓ Local BLIP model configured for backup validation")

# Current API key index for rotation
current_gemini_key_index = 0

# Helper function to get real client IP (handles proxies/load balancers)
def get_client_ip():
    """
    Get the real client IP address, considering proxy headers
    
    Returns:
        Client IP address as string
    """
    # Check if behind a proxy (X-Forwarded-For header)
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For can contain multiple IPs: "client, proxy1, proxy2"
        # The first one is the real client IP
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        # Some proxies use X-Real-IP header
        ip = request.headers.get('X-Real-IP')
    else:
        # Direct connection (no proxy)
        ip = request.remote_addr
    
    return ip

# IP Geolocation function using ip-api.com (45 requests/minute, no API key)
def get_location_from_ip(ip_address):
    """
    Get location from IP address using ip-api.com
    Free tier: 45 requests/minute
    
    Args:
        ip_address: IP address to lookup
        
    Returns:
        Dict with location info or None
    """
    try:
        # Handle local/localhost IPs
        if ip_address in ['127.0.0.1', 'localhost', '::1', None, '']:
            return {
                'city': 'Local',
                'region': 'Local',
                'country': 'Local'
            }
        
        # Handle private IP ranges (RFC 1918) - can't be geolocated
        if ip_address:
            # Check if private IP
            if (ip_address.startswith('192.168.') or 
                ip_address.startswith('10.') or 
                ip_address.startswith('172.16.') or
                ip_address.startswith('172.17.') or
                ip_address.startswith('172.18.') or
                ip_address.startswith('172.19.') or
                ip_address.startswith('172.2') or
                ip_address.startswith('172.30.') or
                ip_address.startswith('172.31.')):
                return {
                    'city': 'Private Network',
                    'region': 'Private Network',
                    'country': 'Private Network'
                }
        
        # Check cache first
        if ip_address in location_cache:
            return location_cache[ip_address]
        
        # Query ip-api.com
        response = requests.get(
            f'http://ip-api.com/json/{ip_address}',
            params={'fields': 'status,country,regionName,city,lat,lon'},
            timeout=3
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                location = {
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('regionName', 'Unknown'),
                    'country': data.get('country', 'Unknown'),
                    'latitude': data.get('lat'),
                    'longitude': data.get('lon')
                }
                # Cache the result
                location_cache[ip_address] = location
                return location
    except Exception as e:
        logger.warning(f"Error getting location for {ip_address}: {e}")
    
    # Return default if lookup fails
    default_location = {
        'city': 'Unknown',
        'region': 'Unknown',
        'country': 'Unknown'
    }
    location_cache[ip_address] = default_location
    return default_location

# Global variables for model and settings
model = None
class_names = []
IMG_HEIGHT = 224
IMG_WIDTH = 224

# Initialize Local BLIP Model for Image Validation
blip_processor = None
blip_model = None

def load_blip_model():
    """
    Load local BLIP model for image captioning and validation
    Uses Salesforce BLIP model stored locally
    """
    global blip_processor, blip_model
    
    if not TRANSFORMERS_AVAILABLE:
        logger.warning("⚠ Transformers not available - cannot load BLIP model")
        return False
    
    try:
        logger.info("📦 Loading local BLIP model...")
        
        # Use smaller BLIP model for faster inference
        model_name = "Salesforce/blip-image-captioning-base"
        
        # Load processor and model
        blip_processor = BlipProcessor.from_pretrained(model_name)
        blip_model = BlipForConditionalGeneration.from_pretrained(model_name)
        
        # Move to CPU (or GPU if available)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        blip_model.to(device)
        blip_model.eval()  # Set to evaluation mode
        
        logger.info(f"✅ BLIP model loaded successfully on {device}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to load BLIP model: {e}")
        return False

# Disease information database
DISEASE_INFO = {
    "Chilli Whitefly": {
        "severity": "Medium",
        "description": "Whiteflies are small, winged insects that suck sap from chilli leaves, causing yellowing, stunted growth, and reduced yield.",
        "symptoms": [
            "Presence of small white flies on leaf undersides",
            "Yellowing and wilting of leaves",
            "Sticky honeydew secretion on leaves",
            "Sooty mold growth on honeydew"
        ],
        "causes": [
            "Hot and humid weather conditions",
            "Poor air circulation",
            "Overcrowding of plants",
            "Lack of natural predators"
        ],
        "treatment": [
            "Use yellow sticky traps to monitor and control populations",
            "Apply neem oil spray (3-5 ml per liter of water)",
            "Use insecticidal soap or horticultural oil",
            "Introduce natural predators like ladybugs",
            "Maintain proper spacing between plants",
            "Remove heavily infested leaves"
        ],
        "prevention": [
            "Regular monitoring of plants",
            "Ensure good air circulation",
            "Avoid over-fertilization with nitrogen",
            "Use reflective mulch to deter whiteflies",
            "Rotate crops annually"
        ],
        "organic_solutions": [
            "Neem oil spray (organic pesticide)",
            "Garlic and chili spray mixture",
            "Soap water solution",
            "Beneficial insects (ladybugs, lacewings)"
        ]
    },
    "Chilli Yellowish": {
        "severity": "High",
        "description": "Leaf yellowing (chlorosis) in chilli plants can result from nutrient deficiencies, water stress, or viral infections.",
        "symptoms": [
            "Yellowing of older or younger leaves",
            "Stunted plant growth",
            "Reduced fruit production",
            "Leaf drop in severe cases"
        ],
        "causes": [
            "Nitrogen deficiency",
            "Iron deficiency (chlorosis)",
            "Overwatering or underwatering",
            "Poor soil drainage",
            "Viral infections",
            "Root damage"
        ],
        "treatment": [
            "Test soil pH and nutrient levels",
            "Apply balanced NPK fertilizer (19-19-19)",
            "For iron deficiency: Apply chelated iron",
            "Improve drainage if waterlogged",
            "Adjust watering schedule",
            "Remove infected plants if viral"
        ],
        "prevention": [
            "Maintain soil pH between 6.0-6.8",
            "Regular fertilization schedule",
            "Proper watering practices",
            "Ensure good drainage",
            "Use disease-free seedlings",
            "Mulch to maintain soil moisture"
        ],
        "organic_solutions": [
            "Compost tea application",
            "Seaweed extract for micronutrients",
            "Bone meal for phosphorus",
            "Fish emulsion for nitrogen",
            "Epsom salt for magnesium"
        ]
    },
    "Chilli healthy": {
        "severity": "None",
        "description": "Your chilli plant is healthy! Continue maintaining good agricultural practices.",
        "symptoms": [
            "Vibrant green leaves",
            "Strong stem structure",
            "Active growth",
            "Good fruit production"
        ],
        "causes": [
            "Proper care and maintenance",
            "Adequate nutrients and water",
            "Disease-free environment"
        ],
        "treatment": [
            "No treatment needed - continue current care routine"
        ],
        "prevention": [
            "Continue regular monitoring",
            "Maintain consistent watering schedule",
            "Apply balanced fertilizer monthly",
            "Prune dead or damaged leaves",
            "Monitor for early signs of pests/diseases"
        ],
        "organic_solutions": [
            "Organic compost application",
            "Mulching to retain moisture",
            "Companion planting (basil, marigold)",
            "Neem oil as preventive spray"
        ]
    },
    "Chilli Anthacnose": {
        "severity": "High",
        "description": "Anthracnose is a serious fungal disease causing fruit rot and significant yield losses in chilli plants.",
        "symptoms": [
            "Circular, sunken lesions on fruits",
            "Dark brown to black spots with concentric rings",
            "Pink to orange spore masses in wet conditions",
            "Premature fruit drop",
            "Leaf spots with yellow halos"
        ],
        "causes": [
            "Colletotrichum fungal species",
            "Warm, humid weather (25-30°C)",
            "Heavy rainfall or overhead irrigation",
            "Infected seeds or plant debris",
            "Wounds on fruits or leaves"
        ],
        "treatment": [
            "Remove and destroy infected fruits and plant parts",
            "Apply copper-based fungicides (Bordeaux mixture)",
            "Use systemic fungicides (Carbendazim, Mancozeb)",
            "Improve air circulation around plants",
            "Avoid overhead irrigation",
            "Apply fungicide sprays every 7-10 days"
        ],
        "prevention": [
            "Use disease-resistant varieties",
            "Ensure proper spacing (45-60 cm)",
            "Avoid working with plants when wet",
            "Practice crop rotation (3-4 years)",
            "Use drip irrigation instead of sprinklers",
            "Remove plant debris after harvest",
            "Treat seeds with hot water (50°C for 25 min)"
        ],
        "organic_solutions": [
            "Neem oil spray (2-3 times per week)",
            "Baking soda solution (1 tbsp per liter)",
            "Garlic extract spray",
            "Trichoderma-based bio-fungicides",
            "Copper sulfate (organic approved)"
        ]
    },
    "Chilli Leaf Curl Virus": {
        "severity": "Very High",
        "description": "Chilli Leaf Curl Virus (ChLCV) is a devastating viral disease transmitted by whiteflies, causing severe crop losses.",
        "symptoms": [
            "Upward or downward curling of leaves",
            "Leaf puckering and distortion",
            "Yellowing of leaf veins",
            "Severe stunting of plant growth",
            "Reduced flowering and fruit set",
            "Small, deformed fruits"
        ],
        "causes": [
            "Begomovirus transmitted by whiteflies",
            "Infected seedlings or transplants",
            "High whitefly populations",
            "Warm weather (25-35°C)",
            "Contaminated agricultural tools"
        ],
        "treatment": [
            "NO CURE - Remove infected plants immediately",
            "Control whitefly vectors aggressively",
            "Apply systemic insecticides (Imidacloprid)",
            "Use yellow sticky traps",
            "Isolate healthy plants from infected areas",
            "Disinfect tools with 10% bleach solution"
        ],
        "prevention": [
            "Use virus-free certified seeds/seedlings",
            "Install insect-proof nets (50-mesh) in nursery",
            "Plant trap crops (marigold) around field edges",
            "Rogue out infected plants early",
            "Control weeds (alternate hosts)",
            "Avoid planting near infected fields",
            "Use reflective mulch to repel whiteflies",
            "Monitor whitefly populations weekly"
        ],
        "organic_solutions": [
            "Neem oil spray (controls whiteflies)",
            "Garlic and chili spray",
            "Soap water solution for whiteflies",
            "Introduce predatory insects",
            "Use kaolin clay as a barrier",
            "Plant resistant varieties if available"
        ]
    }
}

# ============================================
# PLANT PROGNOSIS DATA
# Estimates for life expectancy, yield impact, and next likely disease.
# Values represent the range when disease is unconfirmed (low confidence)
# through fully confirmed (high confidence).
# ============================================
PROGNOSIS_DATA = {
    "Chilli Whitefly": {
        "life_weeks_min": 6,
        "life_weeks_max": 20,
        "life_label": "6–20 weeks remaining (with prompt treatment)",
        "yield_min": 40,
        "yield_max": 65,
        "yield_label": "40–65% of normal yield expected",
        "next_disease": "Chilli Leaf Curl Virus",
        "next_disease_reason": (
            "Whiteflies are the primary vector for Chilli Leaf Curl Virus. "
            "Prolonged infestation dramatically raises the risk of viral transmission to the plant."
        ),
    },
    "Chilli Yellowish": {
        "life_weeks_min": 4,
        "life_weeks_max": 14,
        "life_label": "4–14 weeks remaining (depends on underlying cause)",
        "yield_min": 25,
        "yield_max": 55,
        "yield_label": "25–55% of normal yield expected",
        "next_disease": "Chilli Anthacnose",
        "next_disease_reason": (
            "Nutrient-stressed and chlorotic plants have weakened immunity, "
            "making them prime targets for Anthracnose fungal infection."
        ),
    },
    "Chilli Anthacnose": {
        "life_weeks_min": 2,
        "life_weeks_max": 8,
        "life_label": "2–8 weeks remaining (spreads rapidly without treatment)",
        "yield_min": 10,
        "yield_max": 35,
        "yield_label": "10–35% of normal yield expected",
        "next_disease": "Chilli Yellowish",
        "next_disease_reason": (
            "Anthracnose-damaged tissue disrupts nutrient uptake, "
            "leading to secondary chlorosis (yellowing) as the plant struggles to recover."
        ),
    },
    "Chilli Leaf Curl Virus": {
        "life_weeks_min": 1,
        "life_weeks_max": 4,
        "life_label": "1–4 weeks remaining (highly destructive viral disease)",
        "yield_min": 5,
        "yield_max": 20,
        "yield_label": "5–20% of normal yield expected",
        "next_disease": "Chilli Whitefly",
        "next_disease_reason": (
            "Virally weakened plants attract higher whitefly populations, "
            "creating a destructive reinforcing cycle of infestation and viral spread."
        ),
    },
    "Chilli healthy": {
        "life_weeks_min": 24,
        "life_weeks_max": 52,
        "life_label": "6–12 months (full growing season ahead)",
        "yield_min": 90,
        "yield_max": 100,
        "yield_label": "90–100% of expected yield",
        "next_disease": "Chilli Whitefly",
        "next_disease_reason": (
            "Whitefly is the most common first infestation in healthy chilli crops. "
            "Monitor the undersides of leaves regularly as a preventive measure."
        ),
    },
}


def get_plant_prognosis(disease_name, confidence):
    """
    Compute a confidence-adjusted plant prognosis.

    For diseased plants: higher confidence → worse prognosis (disease is confirmed).
    For healthy plants:  higher confidence → better prognosis (health is confirmed).

    Returns a dict with life_weeks, yield_percentage, life_label,
    yield_label, next_disease, next_disease_reason.
    """
    base = PROGNOSIS_DATA.get(disease_name)
    if not base:
        return None

    factor = max(0.0, min(confidence / 100.0, 1.0))  # clamp 0–1

    if disease_name == "Chilli healthy":
        life_weeks = base["life_weeks_min"] + (base["life_weeks_max"] - base["life_weeks_min"]) * factor
        yield_pct = base["yield_min"] + (base["yield_max"] - base["yield_min"]) * factor
    else:
        # High confidence → disease confirmed → closer to worst-case (min)
        life_weeks = base["life_weeks_max"] - (base["life_weeks_max"] - base["life_weeks_min"]) * factor
        yield_pct = base["yield_max"] - (base["yield_max"] - base["yield_min"]) * factor

    return {
        "life_weeks": round(life_weeks, 1),
        "life_label": base["life_label"],
        "yield_percentage": round(yield_pct, 1),
        "yield_label": base["yield_label"],
        "next_disease": base["next_disease"],
        "next_disease_reason": base["next_disease_reason"],
    }


def load_model_and_classes():
    """Load the trained model and class names"""
    global model, class_names
    
    try:
        # Try loading different model formats with compatibility handling
        model_paths = [
            'best_chilli_disease_model.h5',
            'chilli_disease_detection_model_final.h5',
            'chilli_disease_detection_model_final.keras',
            'chilli_disease_model_saved'
        ]
        
        for model_path in model_paths:
            if os.path.exists(model_path):
                logger.info(f"Loading model from: {model_path}")
                
                # Try multiple loading strategies for compatibility
                try:
                    # Strategy 1: Load with compile=False (skips optimization issues)
                    model = keras.models.load_model(model_path, compile=False)
                    logger.info("Model loaded successfully with compile=False!")
                    
                    # Recompile the model manually
                    model.compile(
                        optimizer='adam',
                        loss='categorical_crossentropy',
                        metrics=['accuracy']
                    )
                    break
                    
                except Exception as e1:
                    logger.warning(f"Failed to load with compile=False: {str(e1)}")
                    
                    try:
                        # Strategy 2: Try loading with TF2 format
                        model = tf.keras.models.load_model(model_path, compile=False)
                        logger.info("Model loaded successfully with TF2 format!")
                        
                        model.compile(
                            optimizer='adam',
                            loss='categorical_crossentropy',
                            metrics=['accuracy']
                        )
                        break
                        
                    except Exception as e2:
                        logger.warning(f"Failed with TF2 format: {str(e2)}")
                        
                        try:
                            # Strategy 3: Load SavedModel format if directory
                            if os.path.isdir(model_path):
                                loaded = tf.saved_model.load(model_path)
                                # Get the inference function
                                if hasattr(loaded, 'signatures'):
                                    # Use default serving signature
                                    infer = loaded.signatures['serving_default']
                                    # Create a wrapper that accepts **kwargs
                                    model = lambda x, **kwargs: infer(tf.constant(x, dtype=tf.float32))
                                else:
                                    model = loaded
                                logger.info("Model loaded as SavedModel!")
                                break
                        except Exception as e3:
                            logger.warning(f"Failed with SavedModel: {str(e3)}")
                            continue
        
        if model is None:
            raise FileNotFoundError(
                "No model file found or all loading strategies failed! "
                "Please ensure you have one of these files: " + 
                ", ".join(model_paths)
            )
        
        # Load class names
        if os.path.exists('class_names.json'):
            with open('class_names.json', 'r') as f:
                class_names = json.load(f)
        else:
            # Default class names if file doesn't exist
            class_names = [
                "Chilli Whitefly",
                "Chilli Yellowish",
                "Chilli healthy",
                "Chilli Anthacnose",
                "Chilli Leaf Curl Virus"
            ]
        
        logger.info(f"Loaded {len(class_names)} classes: {class_names}")
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise


def validate_with_huggingface(image_bytes):
    """
    Use Local BLIP Model for image validation
    Fast, offline validation without API calls
    """
    global blip_processor, blip_model
    
    try:
        # Load BLIP model if not already loaded
        if blip_processor is None or blip_model is None:
            if not load_blip_model():
                logger.warning("BLIP model not available")
                return None
        
        logger.info("🤗 Using local BLIP model for validation...")
        
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # Prepare image for BLIP model
        device = "cuda" if torch.cuda.is_available() else "cpu"
        inputs = blip_processor(image, return_tensors="pt").to(device)
        
        # Generate caption
        with torch.no_grad():
            out = blip_model.generate(**inputs, max_length=50)
        
        caption = blip_processor.decode(out[0], skip_special_tokens=True).lower()
        logger.info(f"BLIP caption: {caption}")
        
        # Check if caption mentions plant, pepper, chilli, leaf, vegetable
        plant_keywords = ['plant', 'pepper', 'chili', 'chilli', 'leaf', 'leaves', 'vegetable', 'capsicum', 'green', 'garden']
        invalid_keywords = ['person', 'people', 'human', 'animal', 'dog', 'cat', 'car', 'building', 'furniture']
        
        has_plant = any(keyword in caption for keyword in plant_keywords)
        has_invalid = any(keyword in caption for keyword in invalid_keywords)
        
        if has_invalid:
            return False, f"Image appears to be: {caption}"
        elif has_plant:
            return True, "Image validated (Local BLIP model)"
        else:
            return False, f"Unclear image content: {caption}"
            
    except Exception as e:
        logger.warning(f"Local BLIP validation failed: {str(e)}")
        return None


def validate_with_local_rules(image_bytes):
    """
    Advanced local validation using multi-factor analysis
    Ultimate fallback when all APIs are exhausted
    
    Analyzes:
    1. Color distribution (green/brown/yellow for plants)
    2. Color variance (organic vs artificial)
    3. Brightness distribution (natural lighting)
    4. Edge patterns (organic shapes vs geometric)
    """
    try:
        logger.info("🔍 Using advanced local validation...")
        
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        original_size = img.size
        
        # Resize for faster processing but keep aspect ratio
        img.thumbnail((300, 300))
        
        pixels = np.array(img)
        height, width, _ = pixels.shape
        total_pixels = height * width
        
        # === ANALYSIS 1: Color Distribution ===
        r_channel = pixels[:, :, 0].flatten()
        g_channel = pixels[:, :, 1].flatten()
        b_channel = pixels[:, :, 2].flatten()
        
        # Count plant-like colors (green, yellow-green, brown, yellow)
        plant_colors = 0
        green_pixels = 0
        brown_yellow_pixels = 0
        
        for i in range(len(r_channel)):
            r, g, b = r_channel[i], g_channel[i], b_channel[i]
            
            # Strong green (healthy leaves)
            if g > r and g > b and g > 40:
                green_pixels += 1
                plant_colors += 1
            # Yellow-green (diseased/aging leaves)
            elif g > b and (g > r * 0.8) and g > 60:
                plant_colors += 1
            # Brown/tan (diseased spots, stems)
            elif 80 < r < 180 and 60 < g < 160 and 30 < b < 120 and abs(r - g) < 60:
                brown_yellow_pixels += 1
                plant_colors += 1
            # Yellowish (chlorosis, disease)
            elif g > 100 and r > 80 and abs(r - g) < 40 and b < 100:
                plant_colors += 1
        
        plant_color_ratio = plant_colors / total_pixels
        green_ratio = green_pixels / total_pixels
        
        logger.info(f"Plant colors: {plant_color_ratio:.2%}, Green: {green_ratio:.2%}")
        
        # === ANALYSIS 2: Color Variance (Organic vs Artificial) ===
        # Natural images have more color variance
        r_std = np.std(r_channel)
        g_std = np.std(g_channel)
        b_std = np.std(b_channel)
        avg_variance = (r_std + g_std + b_std) / 3
        
        logger.info(f"Color variance: {avg_variance:.2f}")
        
        # === ANALYSIS 3: Brightness Distribution ===
        brightness = (r_channel + g_channel + b_channel) / 3
        avg_brightness = np.mean(brightness)
        brightness_std = np.std(brightness)
        
        # Check if image is not too dark or too bright (valid lighting)
        good_lighting = 30 < avg_brightness < 220 and brightness_std > 15
        
        logger.info(f"Brightness: {avg_brightness:.1f}, Std: {brightness_std:.1f}")
        
        # === ANALYSIS 4: Red/White Detection (likely non-plant) ===
        red_pixels = 0
        white_pixels = 0
        black_pixels = 0
        
        for i in range(len(r_channel)):
            r, g, b = r_channel[i], g_channel[i], b_channel[i]
            
            # Strong red (unlikely for chilli leaves)
            if r > 150 and g < 100 and b < 100:
                red_pixels += 1
            # Very white (paper, wall, sky)
            elif r > 200 and g > 200 and b > 200:
                white_pixels += 1
            # Very black (background)
            elif r < 30 and g < 30 and b < 30:
                black_pixels += 1
        
        red_ratio = red_pixels / total_pixels
        white_ratio = white_pixels / total_pixels
        black_ratio = black_pixels / total_pixels
        
        # === SCORING SYSTEM ===
        score = 0
        max_score = 100
        reasons = []
        
        # Plant color analysis (40 points)
        if plant_color_ratio > 0.30:
            score += 40
            reasons.append(f"Strong plant colors ({plant_color_ratio:.1%})")
        elif plant_color_ratio > 0.20:
            score += 30
            reasons.append(f"Moderate plant colors ({plant_color_ratio:.1%})")
        elif plant_color_ratio > 0.10:
            score += 15
            reasons.append(f"Some plant colors ({plant_color_ratio:.1%})")
        
        # Green specifically (25 points)
        if green_ratio > 0.20:
            score += 25
            reasons.append("Good green content")
        elif green_ratio > 0.10:
            score += 15
            reasons.append("Some green content")
        elif green_ratio > 0.05:
            score += 8
        
        # Color variance (15 points)
        if avg_variance > 40:
            score += 15
            reasons.append("Natural color variation")
        elif avg_variance > 25:
            score += 10
        elif avg_variance > 15:
            score += 5
        
        # Lighting quality (10 points)
        if good_lighting:
            score += 10
            reasons.append("Good lighting")
        
        # Penalty for non-plant indicators (10 points deduction each)
        if red_ratio > 0.3:
            score -= 10
            reasons.append("⚠ High red content")
        if white_ratio > 0.5:
            score -= 10
            reasons.append("⚠ Too much white/background")
        if black_ratio > 0.5:
            score -= 10
            reasons.append("⚠ Too much black/dark")
        
        # Image size check (bonus)
        if original_size[0] > 400 and original_size[1] > 400:
            score += 10
            reasons.append("Good image quality")
        
        logger.info(f"Validation score: {score}/{max_score}")
        logger.info(f"Reasons: {', '.join(reasons)}")
        
        # === DECISION ===
        # Threshold: 45 points to pass
        if score >= 45:
            return True, f"Valid plant image (score: {score}/100, {', '.join(reasons[:2])})"
        elif score >= 25:
            # Borderline - accept with warning
            return True, f"Possible plant image (score: {score}/100, please use clear leaf photos)"
        else:
            return False, f"Image doesn't appear to be a chilli plant (score: {score}/100)"
            
    except Exception as e:
        logger.error(f"Local validation failed: {str(e)}")
        # When everything fails, allow through with warning
        return True, "Validation unavailable - proceeding with analysis"


def validate_chilli_image(image_file):
    """
    Multi-tier validation system with automatic fallback:
    1. Try all Gemini API keys (rotate through multiple accounts)
    2. Try Local BLIP Model (fast, offline image validation)
    3. Use local color-based validation (ultimate fallback)
    
    Returns: (is_valid, message)
    """
    global current_gemini_key_index
    
    try:
        # Read and prepare image
        image_file.seek(0)  # Reset file pointer
        img = Image.open(image_file)
        
        # Convert image to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        image_bytes = img_byte_arr.read()
        
        # === TIER 1: Try all Gemini API keys ===
        if GEMINI_API_KEYS:
            model_names = [
                # TIER 1: Highest Accuracy (try these first)
                'models/gemini-2.0-flash-exp',           # Best overall - experimental with image support
                'models/gemini-2.5-pro',                 # Highest tier Pro model
                'models/gemini-2.5-flash-image',         # Image specialist
                
                # TIER 2: Excellent Balance (accuracy + speed)
                'models/gemini-2.0-flash-latest',        # Latest stable Flash
                'models/gemini-pro-latest',              # Latest Pro model
                'models/gemini-2.5-flash',               # Fast and accurate
                
                # TIER 3: Reliable Fallbacks
                'models/gemini-2.0-flash',               # Stable version
                'models/gemini-flash-latest',            # Generic latest
                'models/gemini-2.0-flash-001',           # Specific stable version
                
                # TIER 4: Lite Models (only if others exhausted)
                'models/gemini-2.0-flash-lite',          # Lightweight but still capable
                'models/gemini-2.5-flash-lite',          # Lite with newer tech
            ]
            
            prompt = """Analyze this image carefully and determine if it shows a chilli pepper plant (also known as hot pepper, capsicum, or chile plant) or its leaves.

Respond with ONLY ONE of these exact formats:
- "VALID: This is a chilli plant" (if the image shows any part of a chilli/pepper plant including leaves, fruits, stems, or the whole plant)
- "INVALID: [brief reason]" (if the image does NOT show a chilli plant)

Important:
- Chilli plants have distinctive elongated leaves and can show various conditions (healthy, diseased, damaged)
- Accept images of chilli leaves with spots, yellowing, curling, or other disease symptoms
- Accept images of chilli fruits (peppers)
- Reject images of other vegetables, fruits, animals, people, objects, or non-chilli plants
- Be strict but recognize that diseased chilli leaves may look different from healthy ones

Your response:"""
            
            # Try each API key
            for key_idx, api_key in enumerate(GEMINI_API_KEYS):
                try:
                    gemini_client = genai.Client(api_key=api_key)
                    logger.info(f"🔑 Trying API Key #{key_idx + 1}/{len(GEMINI_API_KEYS)}")
                    
                    # Try each model with this API key
                    for model_name in model_names:
                        try:
                            response = gemini_client.models.generate_content(
                                model=model_name,
                                contents=[
                                    types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
                                    prompt
                                ]
                            )
                            
                            response_text = response.text.strip()
                            logger.info(f"✅ Success! Key #{key_idx + 1}, Model: {model_name}")
                            
                            # Update the key index for next time
                            current_gemini_key_index = key_idx
                            
                            # Parse response
                            if response_text.upper().startswith("VALID"):
                                return True, "Image validated as chilli plant (Gemini API)"
                            else:
                                reason = response_text.split(":", 1)[1].strip() if ":" in response_text else "Not a chilli plant image"
                                return False, reason
                                
                        except Exception as e:
                            error_msg = str(e)
                            if '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg or 'quota' in error_msg.lower():
                                logger.warning(f"⚠ Key #{key_idx + 1}, Model {model_name} quota exhausted")
                                continue
                            else:
                                logger.warning(f"⚠ Key #{key_idx + 1}, Model {model_name} error: {error_msg[:50]}...")
                                continue
                    
                    logger.warning(f"❌ All models exhausted for Key #{key_idx + 1}")
                    
                except Exception as e:
                    logger.warning(f"❌ API Key #{key_idx + 1} failed: {str(e)[:50]}...")
                    continue
            
            logger.warning("❌ All Gemini API keys exhausted - switching to backup methods")
        
        # === TIER 2: Try Local BLIP Model ===
        hf_result = validate_with_huggingface(image_bytes)
        if hf_result is not None:
            logger.info("✅ Local BLIP validation succeeded")
            return hf_result
        
        # === TIER 3: Local validation (ultimate fallback) ===
        logger.info("📍 Using local color-based validation (final fallback)")
        return validate_with_local_rules(image_bytes)
        
    except Exception as e:
        logger.error(f"Critical validation error: {str(e)}")
        # Absolute fallback - allow image through
        return True, "Validation unavailable"


def preprocess_image(image_file):
    """Preprocess the uploaded image for model prediction"""
    try:
        # Read image
        img = Image.open(image_file).convert('RGB')
        
        # Resize to model input size
        img = img.resize((IMG_WIDTH, IMG_HEIGHT))
        
        # Convert to array and normalize
        img_array = np.array(img)
        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array, img
    
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        raise


def predict_disease(img_array):
    """Make prediction using the loaded model"""
    try:
        # Handle different model formats
        if hasattr(model, 'predict'):
            # Keras model with predict method
            predictions = model.predict(img_array, verbose=0)
        elif callable(model):
            # SavedModel format or lambda function
            result = model(img_array)
            
            # Handle different output types from SavedModel
            if isinstance(result, dict):
                # SavedModel signature returns a dict, get the output tensor
                # Common keys: 'output', 'output_0', 'dense', etc.
                for key in ['output', 'output_0', 'dense', 'predictions']:
                    if key in result:
                        predictions = result[key]
                        break
                else:
                    # Get first value if standard keys not found
                    predictions = list(result.values())[0]
            else:
                predictions = result
            
            # Convert TensorFlow tensor to numpy
            if hasattr(predictions, 'numpy'):
                predictions = predictions.numpy()
        else:
            raise ValueError(f"Model type {type(model)} not supported")
        
        # Ensure predictions is numpy array
        if not isinstance(predictions, np.ndarray):
            predictions = np.array(predictions)
        
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx] * 100)
        predicted_class = class_names[predicted_class_idx]
        
        # Get all class probabilities
        all_probabilities = {
            class_names[i]: float(predictions[0][i] * 100) 
            for i in range(len(class_names))
        }
        
        # Sort by probability
        sorted_probs = sorted(all_probabilities.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'predicted_class': predicted_class,
            'confidence': confidence,
            'all_probabilities': all_probabilities,
            'top_3_predictions': sorted_probs[:3]
        }
    
    except Exception as e:
        logger.error(f"Error making prediction: {str(e)}")
        logger.error(f"Model type: {type(model)}")
        logger.error(f"Model callable: {callable(model)}")
        import traceback
        logger.error(traceback.format_exc())
        raise


def get_disease_info_from_db(disease_name):
    """Get disease information from MongoDB (with fallback to DISEASE_INFO dict)"""
    if mongodb and mongodb.connected:
        try:
            disease_doc = mongodb.get_disease(disease_name)
            if disease_doc:
                # Remove MongoDB _id field
                disease_doc.pop('_id', None)
                disease_doc.pop('name', None)
                disease_doc.pop('created_at', None)
                disease_doc.pop('updated_at', None)
                return disease_doc
        except Exception as e:
            logger.warning(f"MongoDB query failed, using fallback: {e}")
    
    # Fallback to dictionary
    return DISEASE_INFO.get(disease_name, {})


def save_prediction_to_mongo(prediction_result, validation_method, validation_message,
                            image_filename=None, user_ip=None, user_agent=None):
    """Save prediction to MongoDB for analytics"""
    if not (mongodb and mongodb.connected):
        return None
    
    try:
        # Get location from IP address
        location = get_location_from_ip(user_ip)
        
        prediction_data = {
            'image_filename': image_filename,
            'predicted_disease': prediction_result['predicted_class'],
            'confidence': prediction_result['confidence'],
            'all_probabilities': prediction_result['all_probabilities'],
            'top_3_predictions': [[item[0], item[1]] for item in prediction_result['top_3_predictions']],
            'validation_method': validation_method,
            'validation_message': validation_message,
            'user_ip': user_ip,
            'user_agent': user_agent,
            'location': location,
            'model_version': '1.0.0',
            'timestamp': datetime.now()
        }
        
        # Add user information if logged in
        if current_user.is_authenticated:
            prediction_data['user_id'] = current_user.id
            prediction_data['user_email'] = current_user.email
            prediction_data['user_type'] = current_user.user_type
        else:
            prediction_data['user_id'] = None
            prediction_data['user_email'] = 'anonymous'
            prediction_data['user_type'] = 'guest'
        
        prediction_id = mongodb.save_prediction(prediction_data)
        return prediction_id
        
    except Exception as e:
        logger.error(f"Failed to save prediction to MongoDB: {e}")
        return None


# ============================================
# AUTHENTICATION ROUTES
# ============================================

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Validate email format
        if '@' not in email or '.' not in email:
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        
        # Validate password length
        if len(password) < 6:
            return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400
        
        # Check if MongoDB is available
        if not mongodb or not mongodb.connected:
            logger.error("MongoDB not available during signup")
            return jsonify({'success': False, 'error': 'Database not available. Please try again later.'}), 503
        
        # Check if user already exists
        try:
            existing_user = mongodb.get_user_by_email(email)
            if existing_user:
                return jsonify({'success': False, 'error': 'Email already registered'}), 409
        except Exception as db_error:
            logger.error(f"Database error checking existing user: {db_error}")
            return jsonify({'success': False, 'error': 'Database error. Please try again.'}), 500
        
        # Hash password
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        except Exception as hash_error:
            logger.error(f"Password hashing error: {hash_error}")
            return jsonify({'success': False, 'error': 'Password processing error'}), 500
        
        # Create user
        try:
            user_id = mongodb.create_user(email, password_hash, 'farmer')
        except Exception as create_error:
            logger.error(f"Database error creating user: {create_error}")
            return jsonify({'success': False, 'error': 'Failed to create account. Please try again.'}), 500
        
        if user_id:
            try:
                # Update last login and set logged in status
                mongodb.update_last_login(email)
                
                # Create user object and login
                user = User(user_id, email, 'farmer')
                session.permanent = True
                login_user(user, remember=True)
                
                logger.info(f"New user registered: {email}")
                
                return jsonify({
                    'success': True,
                    'message': 'Account created successfully',
                    'user': {
                        'id': user_id,
                        'email': email,
                        'user_type': 'farmer'
                    }
                }), 201
            except Exception as login_error:
                logger.error(f"Error logging in new user: {login_error}")
                # User created but login failed - still return success
                return jsonify({
                    'success': True,
                    'message': 'Account created successfully. Please log in.',
                    'user': {
                        'email': email,
                        'user_type': 'farmer'
                    }
                }), 201
        else:
            return jsonify({'success': False, 'error': 'Failed to create account'}), 500
    
    except Exception as e:
        logger.error(f"Error in signup: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Check if MongoDB is available
        if not mongodb or not mongodb.connected:
            logger.error("MongoDB not available during login")
            return jsonify({'success': False, 'error': 'Database not available. Please try again later.'}), 503
        
        # Get user from database
        try:
            user_data = mongodb.get_user_by_email(email)
        except Exception as db_error:
            logger.error(f"Database error during login: {db_error}")
            return jsonify({'success': False, 'error': 'Database error. Please try again.'}), 500
        
        if not user_data:
            logger.warning(f"Login attempt for non-existent user: {email}")
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Verify password
        try:
            password_match = bcrypt.checkpw(password.encode('utf-8'), user_data['password'].encode('utf-8'))
        except Exception as verify_error:
            logger.error(f"Password verification error: {verify_error}")
            return jsonify({'success': False, 'error': 'Authentication error'}), 500
        
        if password_match:
            try:
                # Update last login
                mongodb.update_last_login(email)
                
                # Create user object and login
                user = User(str(user_data['_id']), user_data['email'], user_data['user_type'])
                session.permanent = True
                login_user(user, remember=True)
                
                # Log based on user type
                if user_data['user_type'] == 'admin':
                    logger.info(f"Admin user logged in successfully: {email}")
                else:
                    logger.info(f"User logged in successfully: {email}")
                
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'user': {
                        'id': str(user_data['_id']),
                        'email': user_data['email'],
                        'user_type': user_data['user_type']
                    }
                }), 200
            except Exception as login_error:
                logger.error(f"Error during login process: {login_error}")
                return jsonify({'success': False, 'error': 'Login failed'}), 500
        else:
            logger.warning(f"Invalid password for user: {email}")
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@app.route('/api/auth/logout', methods=['POST', 'GET'])
def logout():
    """User logout endpoint"""
    try:
        if current_user.is_authenticated:
            # Update logout status in database
            if mongodb and mongodb.connected:
                mongodb.update_logout_status(current_user.email)
            
            logout_user()
            return jsonify({
                'success': True,
                'message': 'Logged out successfully'
            }), 200
        else:
            return jsonify({
                'success': True,
                'message': 'Already logged out'
            }), 200
    except Exception as e:
        logger.error(f"Error in logout: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@app.route('/api/auth/delete-account', methods=['DELETE'])
@login_required
def delete_account():
    """Delete user account endpoint"""
    try:
        # Admins cannot delete their account
        if current_user.user_type == 'admin':
            return jsonify({'success': False, 'error': 'Admin accounts cannot be deleted'}), 403
        
        # Check if MongoDB is available
        if not mongodb or not mongodb.connected:
            logger.error("MongoDB not available during account deletion")
            return jsonify({'success': False, 'error': 'Database not available. Please try again later.'}), 503
        
        # Get user email before logout
        email = current_user.email
        user_id = current_user.id
        
        # Delete user from database
        try:
            deleted = mongodb.delete_user(email)
            if deleted:
                # Logout user
                logout_user()
                
                logger.info(f"User account deleted: {email}")
                
                return jsonify({
                    'success': True,
                    'message': 'Account deleted successfully'
                }), 200
            else:
                logger.error(f"Failed to delete user from database: {email}")
                return jsonify({'success': False, 'error': 'Failed to delete account. User may not exist.'}), 500
        except Exception as db_error:
            logger.error(f"Database error during account deletion: {db_error}")
            return jsonify({'success': False, 'error': 'Database error. Please try again.'}), 500
    
    except Exception as e:
        logger.error(f"Error in delete account: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Check authentication status"""
    try:
        if current_user.is_authenticated:
            return jsonify({
                'success': True,
                'authenticated': True,
                'user': {
                    'id': current_user.id,
                    'email': current_user.email,
                    'user_type': current_user.user_type
                }
            }), 200
        else:
            return jsonify({
                'success': True,
                'authenticated': False
            }), 200
    except Exception as e:
        logger.error(f"Error checking auth status: {str(e)}")
        return jsonify({
            'success': True,
            'authenticated': False
        }), 200


# ============================================
# MAIN ROUTES
# ============================================

# Routes
@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/predict', methods=['POST'])
@login_required
def api_predict():
    """API endpoint for disease prediction"""
    try:
        # Check if image file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'error': 'Invalid file type. Use PNG, JPG, or JPEG'}), 400
        
        # Validate that the image contains a chilli plant using Gemini API
        is_valid, validation_message = validate_chilli_image(file)
        
        if not is_valid:
            logger.warning(f"Image validation failed: {validation_message}")
            return jsonify({
                'success': False,
                'error': 'Invalid Image',
                'message': f'This does not appear to be a chilli plant image. {validation_message}',
                'suggestion': 'Please upload a clear image of a chilli plant leaf or the whole plant.'
            }), 400
        
        logger.info(f"Image validation passed: {validation_message}")
        
        # Reset file pointer after validation
        file.seek(0)
        
        # Preprocess image
        img_array, original_img = preprocess_image(file)
        
        # Make prediction
        prediction_result = predict_disease(img_array)
        
        # Get disease information (from MongoDB or fallback)
        disease_name = prediction_result['predicted_class']
        disease_data = get_disease_info_from_db(disease_name)
        
        # Save prediction to MongoDB (capture real client IP)
        user_ip = get_client_ip()
        user_agent = request.headers.get('User-Agent', '')[:500]
        prediction_id = save_prediction_to_mongo(
            prediction_result,
            validation_message.split('(')[1].rstrip(')') if '(' in validation_message else 'unknown',
            validation_message,
            file.filename,
            user_ip,
            user_agent
        )
        
        # Compute plant prognosis
        prognosis = get_plant_prognosis(disease_name, prediction_result['confidence'])

        # Prepare response
        response = {
            'success': True,
            'prediction': prediction_result,
            'disease_info': disease_data,
            'prognosis': prognosis,
            'timestamp': datetime.now().isoformat(),
            'model_version': '1.0.0',
            'prediction_id': prediction_id
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/diseases', methods=['GET'])
def get_diseases():
    """Get all disease information"""
    # Try MongoDB first
    if mongodb and mongodb.connected:
        try:
            diseases_list = mongodb.get_all_diseases()
            diseases_dict = {}
            for disease in diseases_list:
                name = disease.pop('name')
                disease.pop('_id', None)
                disease.pop('created_at', None)
                disease.pop('updated_at', None)
                diseases_dict[name] = disease
            
            return jsonify({
                'success': True,
                'diseases': diseases_dict,
                'total_diseases': len(diseases_dict),
                'source': 'mongodb'
            })
        except Exception as e:
            logger.warning(f"MongoDB query failed: {e}")
    
    # Fallback to dictionary
    return jsonify({
        'success': True,
        'diseases': DISEASE_INFO,
        'total_diseases': len(DISEASE_INFO),
        'source': 'fallback'
    })


@app.route('/api/disease/<disease_name>', methods=['GET'])
def get_disease_info(disease_name):
    """Get specific disease information"""
    disease_data = get_disease_info_from_db(disease_name)
    
    if disease_data:
        return jsonify({
            'success': True,
            'disease_name': disease_name,
            'info': disease_data
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Disease not found'
        }), 404


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    mongodb_status = 'not_configured'
    mongodb_details = {}
    
    if mongodb:
        mongodb_status = 'connected' if mongodb.connected else 'disconnected'
        if mongodb.connected:
            try:
                # Get database stats
                mongodb_details = {
                    'database': mongodb.db.name,
                    'collections': mongodb.db.list_collection_names(),
                    'total_users': mongodb.count_users(),
                    'total_diseases': mongodb.db.diseases.count_documents({}),
                    'total_predictions': mongodb.count_predictions()
                }
            except Exception as e:
                logger.warning(f"Could not fetch MongoDB details: {e}")
                mongodb_details = {'error': 'Could not fetch details'}
    
    health_data = {
        'status': 'healthy',
        'model_loaded': model is not None,
        'classes_loaded': len(class_names) > 0,
        'num_classes': len(class_names),
        'mongodb_status': mongodb_status,
        'mongodb_details': mongodb_details,
        'auth_system': {
            'flask_login': 'enabled',
            'session_lifetime': '7 days',
            'admin_stored_in_db': True
        },
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(health_data)


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@app.route('/diseases')
def diseases():
    """Diseases page"""
    return render_template('diseases.html')


@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    """Handle contact form submission"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['name', 'email', 'subject', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False, 
                    'message': f'{field.capitalize()} is required'
                }), 400
        
        # Email validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({
                'success': False,
                'message': 'Please provide a valid email address'
            }), 400
        
        # Store in MongoDB (optional - add if you want to save messages)
        if mongodb and mongodb.db is not None:
            contact_data = {
                'name': data['name'],
                'email': data['email'],
                'subject': data['subject'],
                'message': data['message'],
                'timestamp': datetime.now(),
                'status': 'new'
            }
            mongodb.db.contact_messages.insert_one(contact_data)
        
        # Send email notification
        try:
            if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
                # Email to you (admin)
                msg = Message(
                    subject=f"New Contact Form Submission: {data['subject']}",
                    recipients=[app.config['MAIL_USERNAME']],  # Your Gmail
                    body=f"""
New message from your Chilli Care contact form:

Name: {data['name']}
Email: {data['email']}
Subject: {data['subject']}

Message:
{data['message']}

---
Received at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    """.strip()
                )
                mail.send(msg)
                logger.info(f"Contact form email sent to admin from {data['email']}")
            else:
                logger.warning("Email credentials not configured - message saved to database only")
        except Exception as email_error:
            logger.error(f"Failed to send email: {str(email_error)}")
            # Don't fail the request if email fails - message is still saved to DB
        
        logger.info(f"Contact form submission from {data['email']}: {data['subject']}")
        
        return jsonify({
            'success': True,
            'message': 'Thank you for contacting us! We\'ll get back to you soon.'
        }), 200
        
    except Exception as e:
        logger.error(f"Contact form error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Sorry, there was an error submitting your message. Please try again.'
        }), 500


# ============================================
# NOTIFICATION ENDPOINTS
# ============================================

@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    """Get notifications for the logged-in user"""
    try:
        limit = int(request.args.get('limit', 20))
        skip = int(request.args.get('skip', 0))
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        notification_type = request.args.get('type')
        
        if not mongodb or not mongodb.connected:
            return jsonify({
                'success': False,
                'error': 'Database not available'
            }), 503
        
        notifications = mongodb.get_user_notifications(
            current_user.email,
            limit=limit,
            skip=skip,
            unread_only=unread_only,
            notification_type=notification_type
        )
        
        # Convert ObjectId to string for JSON serialization
        for notif in notifications:
            notif['_id'] = str(notif['_id'])
            notif['created_at'] = notif['created_at'].isoformat()
        
        unread_count = mongodb.count_unread_notifications(current_user.email)
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'unread_count': unread_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching notifications: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch notifications'
        }), 500


@app.route('/api/notifications/count', methods=['GET'])
@login_required
def get_notification_count():
    """Get unread notification count for the logged-in user"""
    try:
        if not mongodb or not mongodb.connected:
            return jsonify({
                'success': False,
                'error': 'Database not available'
            }), 503
        
        unread_count = mongodb.count_unread_notifications(current_user.email)
        
        return jsonify({
            'success': True,
            'unread_count': unread_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error counting notifications: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to count notifications'
        }), 500


@app.route('/api/notifications/<notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    try:
        if not mongodb or not mongodb.connected:
            return jsonify({
                'success': False,
                'error': 'Database not available'
            }), 503
        
        success = mongodb.mark_notification_read(notification_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Notification marked as read'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Notification not found'
            }), 404
        
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to mark notification as read'
        }), 500


@app.route('/api/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read for the logged-in user"""
    try:
        if not mongodb or not mongodb.connected:
            return jsonify({
                'success': False,
                'error': 'Database not available'
            }), 503
        
        count = mongodb.mark_all_notifications_read(current_user.email)
        
        return jsonify({
            'success': True,
            'message': f'Marked {count} notifications as read',
            'count': count
        }), 200
        
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to mark notifications as read'
        }), 500


@app.route('/api/admin/notifications/broadcast', methods=['POST'])
@login_required
def broadcast_notification():
    """
    Admin endpoint to broadcast a notification to all users or filtered users
    Requires admin privileges
    """
    try:
        # Check if user is admin
        if current_user.user_type != 'admin':
            return jsonify({
                'success': False,
                'error': 'Admin privileges required'
            }), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        title = data.get('title')
        message = data.get('message')
        notification_type = data.get('type', 'system_update')
        user_type_filter = data.get('user_type_filter')  # 'farmer', 'admin', or None
        
        if not title or not message:
            return jsonify({
                'success': False,
                'error': 'Title and message are required'
            }), 400
        
        if not mongodb or not mongodb.connected:
            return jsonify({
                'success': False,
                'error': 'Database not available'
            }), 503
        
        count = mongodb.broadcast_notification(
            notification_type=notification_type,
            title=title,
            message=message,
            metadata=data.get('metadata'),
            user_type_filter=user_type_filter
        )
        
        return jsonify({
            'success': True,
            'message': f'Notification sent to {count} users',
            'count': count
        }), 200
        
    except Exception as e:
        logger.error(f"Error broadcasting notification: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to broadcast notification'
        }), 500


@app.route('/privacy')
def privacy():
    """Privacy Policy page"""
    return render_template('privacy.html')


@app.route('/terms')
def terms():
    """Terms of Service page"""
    return render_template('terms.html')


@app.route('/faqs')
def faqs():
    """FAQs page"""
    return render_template('faqs.html')


@app.route('/analytics')
def analytics():
    """Analytics page"""
    return render_template('analytics.html')


@app.route('/docs')
def documentation():
    """API documentation page"""
    return render_template('docs.html')


@app.route('/responsive-test')
def responsive_test():
    """Responsive design test page"""
    return render_template('responsive-test.html')


@app.route('/camera-test')
def camera_test():
    """Camera feature test page"""
    return render_template('camera-test.html')


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard page (admin only)"""
    if current_user.user_type != 'admin':
        return redirect('/')
    return render_template('admin_dashboard.html')


@app.route('/api/admin/analytics', methods=['GET'])
@login_required
def get_admin_analytics():
    """Get admin analytics data (admin only)"""
    if current_user.user_type != 'admin':
        return jsonify({
            'success': False,
            'error': 'Unauthorized'
        }), 403
    
    if not (mongodb and mongodb.connected):
        return jsonify({
            'success': False,
            'error': 'MongoDB not configured'
        }), 503
    
    try:
        # Get time period from query params (default: last 30 days)
        from datetime import datetime, timedelta
        period = request.args.get('period', '30')
        
        # Calculate date range
        if period == 'all':
            start_date = None
        else:
            days = int(period)
            start_date = datetime.now() - timedelta(days=days)
        
        # Get all predictions
        query = {}
        if start_date:
            query['timestamp'] = {'$gte': start_date}
        
        predictions = list(mongodb.db.predictions.find(query))
        
        # Calculate statistics
        total_detections = len(predictions)
        
        # Count by disease (excluding healthy)
        disease_counts = {}
        healthy_count = 0
        
        for pred in predictions:
            disease = pred.get('predicted_disease', 'Unknown')
            # Check if disease contains 'healthy' (case-insensitive)
            if 'healthy' in disease.lower():
                healthy_count += 1
            else:
                disease_counts[disease] = disease_counts.get(disease, 0) + 1
        
        # Find most and least common diseases (excluding healthy)
        most_common = None
        most_common_count = 0
        least_common = None
        least_common_count = float('inf')
        
        for disease, count in disease_counts.items():
            if count > most_common_count:
                most_common = disease
                most_common_count = count
            if count < least_common_count:
                least_common = disease
                least_common_count = count
        
        # Prepare disease distribution data
        disease_distribution = []
        for disease, count in sorted(disease_counts.items(), key=lambda x: x[1], reverse=True):
            disease_distribution.append({
                'disease': disease,
                'count': count
            })
        
        # Get all predictions overview (recent)
        recent_predictions = sorted(predictions, key=lambda x: x.get('timestamp', datetime.min), reverse=True)[:10]
        
        predictions_overview = []
        for pred in recent_predictions:
            predictions_overview.append({
                'disease': pred.get('predicted_disease', 'Unknown'),
                'confidence': round(pred.get('confidence', 0), 2),
                'timestamp': pred.get('timestamp').isoformat() if pred.get('timestamp') else None,
                'location': pred.get('location', {}).get('city', 'Unknown')
            })
        
        return jsonify({
            'success': True,
            'data': {
                'total_detections': total_detections - healthy_count,  # Exclude healthy from total diseases
                'healthy_plants': healthy_count,
                'most_common': {
                    'disease': most_common if most_common else '-',
                    'count': most_common_count if most_common else 0
                },
                'least_common': {
                    'disease': least_common if least_common else '-',
                    'count': least_common_count if least_common and least_common_count != float('inf') else 0
                },
                'disease_distribution': disease_distribution,
                'recent_predictions': predictions_overview
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching admin analytics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/mapping', methods=['GET'])
@login_required
def get_admin_mapping():
    """Get location mapping data for admin (admin only)"""
    if current_user.user_type != 'admin':
        return jsonify({
            'success': False,
            'error': 'Unauthorized'
        }), 403
    
    if not (mongodb and mongodb.connected):
        return jsonify({
            'success': False,
            'error': 'MongoDB not configured'
        }), 503
    
    try:
        # Get filter parameters
        city_filter = request.args.get('city', None)
        region_filter = request.args.get('region', None)
        country_filter = request.args.get('country', None)
        
        # Build query
        query = {}
        
        # Only include predictions with valid location data
        query['location'] = {'$exists': True}
        
        # Apply filters
        if city_filter:
            query['location.city'] = city_filter
        if region_filter:
            query['location.region'] = region_filter
        if country_filter:
            query['location.country'] = country_filter
        
        # Get all predictions with location
        predictions = list(mongodb.db.predictions.find(query))
        
        # Format locations for map
        locations = []
        for pred in predictions:
            location = pred.get('location', {})
            
            # Skip if no lat/lon or invalid locations
            if not location.get('latitude') or not location.get('longitude'):
                continue
            
            city = location.get('city', 'Unknown')
            # Skip invalid/local/private locations
            if city in ['Unknown', 'Local', 'Private Network']:
                continue
            
            locations.append({
                'latitude': location.get('latitude'),
                'longitude': location.get('longitude'),
                'city': city,
                'region': location.get('region', 'Unknown'),
                'country': location.get('country', 'Unknown'),
                'disease': pred.get('predicted_disease', 'Unknown'),
                'confidence': pred.get('confidence', 0),
                'timestamp': pred.get('timestamp').isoformat() if pred.get('timestamp') else None
            })
        
        # Get unique filter options
        cities = sorted(list(set([loc['city'] for loc in locations])))
        regions = sorted(list(set([loc['region'] for loc in locations])))
        countries = sorted(list(set([loc['country'] for loc in locations])))
        
        # Calculate statistics by location
        location_stats = {}
        for loc in locations:
            key = f"{loc['city']}, {loc['region']}, {loc['country']}"
            if key not in location_stats:
                location_stats[key] = {
                    'city': loc['city'],
                    'region': loc['region'],
                    'country': loc['country'],
                    'latitude': loc['latitude'],
                    'longitude': loc['longitude'],
                    'count': 0,
                    'diseases': {}
                }
            location_stats[key]['count'] += 1
            
            disease = loc['disease']
            if disease not in location_stats[key]['diseases']:
                location_stats[key]['diseases'][disease] = 0
            location_stats[key]['diseases'][disease] += 1
        
        return jsonify({
            'success': True,
            'data': {
                'locations': list(location_stats.values()),
                'filters': {
                    'cities': cities,
                    'regions': regions,
                    'countries': countries
                },
                'total_locations': len(location_stats),
                'total_predictions': len(locations)
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching mapping data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/history', methods=['GET'])
def get_prediction_history():
    """Get prediction history with pagination"""
    if not (mongodb and mongodb.connected):
        return jsonify({
            'success': False,
            'error': 'MongoDB not configured'
        }), 503
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        disease_filter = request.args.get('disease', None)
        
        # Calculate skip
        skip = (page - 1) * per_page
        
        # Get predictions
        predictions = mongodb.get_predictions(limit=per_page, skip=skip, disease_filter=disease_filter)
        total = mongodb.count_predictions(disease_filter=disease_filter)
        
        # Convert ObjectId to string
        for pred in predictions:
            pred['_id'] = str(pred['_id'])
            if 'timestamp' in pred:
                pred['timestamp'] = pred['timestamp'].isoformat()
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        })
        
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Get analytics summary"""
    if not (mongodb and mongodb.connected):
        return jsonify({
            'success': False,
            'error': 'MongoDB not configured'
        }), 503
    
    try:
        # Get statistics
        total_predictions = mongodb.count_predictions()
        disease_stats = mongodb.get_disease_statistics()
        recent_count = mongodb.get_recent_predictions_count(days=7)
        today_count = mongodb.get_recent_predictions_count(days=1)
        
        # Process disease stats
        by_disease = []
        for stat in disease_stats:
            by_disease.append({
                'disease': stat['_id'],
                'count': stat['count'],
                'avg_confidence': round(stat['avg_confidence'], 2)
            })
        
        return jsonify({
            'success': True,
            'summary': {
                'total_predictions': total_predictions,
                'today_predictions': today_count,
                'last_7_days': recent_count,
                'by_disease': by_disease
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching analytics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/analytics/daily', methods=['GET'])
def get_daily_analytics():
    """Get daily analytics"""
    if not (mongodb and mongodb.connected):
        return jsonify({
            'success': False,
            'error': 'MongoDB not configured'
        }), 503
    
    try:
        days = request.args.get('days', 30, type=int)
        
        # Get daily statistics
        daily_data = mongodb.get_daily_statistics(days=days)
        
        # Format response
        daily_stats = []
        for stat in daily_data:
            daily_stats.append({
                'date': stat['_id'],
                'count': stat['count']
            })
        
        return jsonify({
            'success': True,
            'daily_stats': daily_stats
        })
        
    except Exception as e:
        logger.error(f"Error fetching daily analytics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/user/predictions', methods=['GET'])
@login_required
def get_user_predictions():
    """Get logged-in user's prediction history"""
    if not (mongodb and mongodb.connected):
        return jsonify({
            'success': False,
            'error': 'MongoDB not configured'
        }), 503
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Calculate skip
        skip = (page - 1) * per_page
        
        # Get user's predictions
        predictions = mongodb.get_user_predictions(
            user_id=current_user.id,
            limit=per_page,
            skip=skip
        )
        
        total = mongodb.count_user_predictions(user_id=current_user.id)
        
        # Convert ObjectId to string and format timestamps
        for pred in predictions:
            pred['_id'] = str(pred['_id'])
            if 'timestamp' in pred:
                pred['timestamp'] = pred['timestamp'].isoformat()
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        })
        
    except Exception as e:
        logger.error(f"Error fetching user predictions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/user/statistics', methods=['GET'])
@login_required
def get_user_statistics():
    """Get logged-in user's prediction statistics"""
    if not (mongodb and mongodb.connected):
        return jsonify({
            'success': False,
            'error': 'MongoDB not configured'
        }), 503
    
    try:
        # Get user's disease statistics
        disease_stats = mongodb.get_user_disease_statistics(user_id=current_user.id)
        
        # Get total predictions count
        total_predictions = mongodb.count_user_predictions(user_id=current_user.id)
        
        # Format disease statistics
        formatted_stats = []
        for stat in disease_stats:
            formatted_stats.append({
                'disease': stat['_id'],
                'count': stat['count'],
                'avg_confidence': round(stat['avg_confidence'], 2),
                'max_confidence': round(stat['max_confidence'], 2),
                'min_confidence': round(stat['min_confidence'], 2),
                'last_prediction': stat['last_prediction'].isoformat() if stat.get('last_prediction') else None
            })
        
        return jsonify({
            'success': True,
            'total_predictions': total_predictions,
            'disease_stats': formatted_stats,
            'user': {
                'email': current_user.email,
                'user_type': current_user.user_type
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching user statistics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/dashboard', methods=['GET'])
@login_required
def get_admin_dashboard():
    """Get admin dashboard data (admin only)"""
    if current_user.user_type != 'admin':
        return jsonify({
            'success': False,
            'error': 'Unauthorized - Admin access required'
        }), 403
    
    if not (mongodb and mongodb.connected):
        return jsonify({
            'success': False,
            'error': 'MongoDB not configured'
        }), 503
    
    try:
        # Get comprehensive statistics
        total_users = mongodb.count_users()
        total_farmers = mongodb.count_users(user_type='farmer')
        total_predictions = mongodb.count_predictions()
        unique_locations = mongodb.count_unique_locations()
        recent_predictions = mongodb.get_recent_predictions_count(days=7)
        
        # Get disease statistics
        disease_stats = mongodb.get_disease_statistics()
        
        # Format disease statistics
        formatted_disease_stats = []
        for stat in disease_stats:
            formatted_disease_stats.append({
                'disease': stat['_id'],
                'count': stat['count'],
                'avg_confidence': round(stat['avg_confidence'], 2),
                'max_confidence': round(stat['max_confidence'], 2),
                'min_confidence': round(stat['min_confidence'], 2)
            })
        
        # Get recent users
        recent_users = mongodb.get_all_users(skip=0, limit=5)
        
        # Format user data (remove sensitive info)
        formatted_users = []
        for user in recent_users:
            formatted_users.append({
                '_id': str(user['_id']),
                'email': user['email'],
                'user_type': user['user_type'],
                'created_at': user['created_at'].isoformat() if user.get('created_at') else None,
                'last_login': user['last_login'].isoformat() if user.get('last_login') else None
            })
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_users': total_users,
                'total_farmers': total_farmers,
                'total_predictions': total_predictions,
                'unique_locations': unique_locations,
                'recent_predictions_7d': recent_predictions
            },
            'disease_stats': formatted_disease_stats,
            'recent_users': formatted_users
        })
        
    except Exception as e:
        logger.error(f"Error fetching admin dashboard: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/users', methods=['GET'])
@login_required
def get_admin_users():
    """Get all users for admin dashboard (admin only)"""
    if current_user.user_type != 'admin':
        return jsonify({
            'success': False,
            'error': 'Unauthorized - Admin access required'
        }), 403
    
    if not (mongodb and mongodb.connected):
        return jsonify({
            'success': False,
            'error': 'MongoDB not configured'
        }), 503
    
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)
        skip = (page - 1) * per_page
        
        # Get all users
        all_users = mongodb.get_all_users(skip=skip, limit=per_page)
        total_users = mongodb.count_users()
        
        # Format user data (remove password)
        formatted_users = []
        for user in all_users:
            formatted_users.append({
                '_id': str(user['_id']),
                'email': user['email'],
                'user_type': user['user_type'],
                'created_at': user['created_at'].isoformat() if user.get('created_at') else None,
                'last_login': user['last_login'].isoformat() if user.get('last_login') else None,
                'is_logged_in': user.get('is_logged_in', False)
            })
        
        return jsonify({
            'success': True,
            'users': formatted_users,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_users,
                'total_pages': (total_users + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/predictions', methods=['GET'])
@login_required
def get_admin_predictions():
    """Get predictions for admin dashboard (admin only)"""
    if current_user.user_type != 'admin':
        return jsonify({
            'success': False,
            'error': 'Unauthorized - Admin access required'
        }), 403
    
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        skip = (page - 1) * limit
        
        # Get filter parameters
        disease_filter = request.args.get('disease', '')
        user_type_filter = request.args.get('user_type', '')
        confidence_filter = request.args.get('confidence', '')
        search_query = request.args.get('search', '')
        
        if not mongodb or not mongodb.connected:
            return jsonify({
                'success': False,
                'error': 'Database not connected'
            }), 500
        
        # Build query
        query = {}
        
        if disease_filter:
            query['predicted_disease'] = disease_filter
        
        if user_type_filter:
            query['user_type'] = user_type_filter
        
        # Confidence filter
        if confidence_filter:
            if confidence_filter == 'high':
                query['confidence'] = {'$gte': 90}
            elif confidence_filter == 'medium':
                query['confidence'] = {'$gte': 70, '$lt': 90}
            elif confidence_filter == 'low':
                query['confidence'] = {'$lt': 70}
        
        # Search query (search in disease, email, location)
        if search_query:
            query['$or'] = [
                {'predicted_disease': {'$regex': search_query, '$options': 'i'}},
                {'user_email': {'$regex': search_query, '$options': 'i'}},
                {'location.city': {'$regex': search_query, '$options': 'i'}},
                {'location.region': {'$regex': search_query, '$options': 'i'}},
                {'location.country': {'$regex': search_query, '$options': 'i'}}
            ]
        
        # Get predictions from database
        predictions_cursor = mongodb.db.predictions.find(query)\
            .sort("timestamp", -1)\
            .skip(skip)\
            .limit(limit)
        
        predictions = list(predictions_cursor)
        total_count = mongodb.db.predictions.count_documents(query)
        
        # Format predictions
        formatted_predictions = []
        for pred in predictions:
            # Format location
            location_str = 'Unknown'
            if 'location' in pred and pred['location']:
                loc = pred['location']
                location_parts = []
                if loc.get('city'):
                    location_parts.append(loc['city'])
                if loc.get('region'):
                    location_parts.append(loc['region'])
                if loc.get('country'):
                    location_parts.append(loc['country'])
                location_str = ', '.join(location_parts) if location_parts else 'Unknown'
            
            formatted_predictions.append({
                '_id': str(pred['_id']),
                'timestamp': pred.get('timestamp').isoformat() if pred.get('timestamp') else None,
                'user_email': pred.get('user_email', 'anonymous'),
                'user_type': pred.get('user_type', 'guest'),
                'predicted_disease': pred.get('predicted_disease', 'Unknown'),
                'confidence': round(pred.get('confidence', 0), 2),
                'location': location_str,
                'location_data': pred.get('location', {}),
                'validation_method': pred.get('validation_method', 'None'),
                'validation_message': pred.get('validation_message', ''),
                'image_filename': pred.get('image_filename'),
                'top_3_predictions': pred.get('top_3_predictions', [])
            })
        
        # Calculate statistics
        all_predictions = list(mongodb.db.predictions.find({}))
        total_predictions = len(all_predictions)
        
        # Calculate average confidence
        avg_confidence = 0
        if all_predictions:
            total_conf = sum(p.get('confidence', 0) for p in all_predictions)
            avg_confidence = round(total_conf / total_predictions, 2)
        
        # Count healthy vs diseased (check both formats)
        healthy_count = mongodb.db.predictions.count_documents({
            '$or': [
                {'predicted_disease': 'Chilli___healthy'},
                {'predicted_disease': 'Chilli healthy'}
            ]
        })
        diseased_count = total_predictions - healthy_count
        
        return jsonify({
            'success': True,
            'predictions': formatted_predictions,
            'pagination': {
                'total': total_count,
                'page': page,
                'limit': limit,
                'pages': (total_count + limit - 1) // limit if total_count > 0 else 1
            },
            'statistics': {
                'total_predictions': total_predictions,
                'avg_confidence': avg_confidence,
                'healthy_count': healthy_count,
                'diseased_count': diseased_count
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching predictions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/diseases', methods=['GET'])
@login_required
def get_admin_diseases():
    """Get all diseases for admin dashboard (admin only)"""
    if current_user.user_type != 'admin':
        return jsonify({
            'success': False,
            'error': 'Unauthorized - Admin access required'
        }), 403
    
    try:
        # First, check if diseases exist in MongoDB
        if mongodb and mongodb.connected:
            diseases_from_db = mongodb.get_all_diseases()
            
            # If diseases exist in DB, return them
            if diseases_from_db:
                formatted_diseases = []
                for disease in diseases_from_db:
                    disease_dict = {
                        '_id': str(disease['_id']),
                        'name': disease.get('name'),
                        'severity': disease.get('severity'),
                        'description': disease.get('description'),
                        'symptoms': disease.get('symptoms', []),
                        'causes': disease.get('causes', []),
                        'treatment': disease.get('treatment', []),
                        'prevention': disease.get('prevention', []),
                        'organic_solutions': disease.get('organic_solutions', []),
                        'created_at': disease['created_at'].isoformat() if disease.get('created_at') else None,
                        'updated_at': disease['updated_at'].isoformat() if disease.get('updated_at') else None
                    }
                    formatted_diseases.append(disease_dict)
                
                return jsonify({
                    'success': True,
                    'diseases': formatted_diseases,
                    'source': 'database'
                })
            else:
                # If no diseases in DB, initialize from DISEASE_INFO
                logger.info("Initializing diseases in database from DISEASE_INFO")
                for disease_name, disease_data in DISEASE_INFO.items():
                    disease_doc = {
                        'name': disease_name,
                        **disease_data
                    }
                    mongodb.insert_disease(disease_doc)
                
                # Fetch again from DB
                diseases_from_db = mongodb.get_all_diseases()
                formatted_diseases = []
                for disease in diseases_from_db:
                    disease_dict = {
                        '_id': str(disease['_id']),
                        'name': disease.get('name'),
                        'severity': disease.get('severity'),
                        'description': disease.get('description'),
                        'symptoms': disease.get('symptoms', []),
                        'causes': disease.get('causes', []),
                        'treatment': disease.get('treatment', []),
                        'prevention': disease.get('prevention', []),
                        'organic_solutions': disease.get('organic_solutions', []),
                        'created_at': disease['created_at'].isoformat() if disease.get('created_at') else None,
                        'updated_at': disease['updated_at'].isoformat() if disease.get('updated_at') else None
                    }
                    formatted_diseases.append(disease_dict)
                
                return jsonify({
                    'success': True,
                    'diseases': formatted_diseases,
                    'source': 'database'
                })
        else:
            # MongoDB not available, return from DISEASE_INFO
            formatted_diseases = []
            for disease_name, disease_data in DISEASE_INFO.items():
                formatted_diseases.append({
                    'name': disease_name,
                    **disease_data
                })
            
            return jsonify({
                'success': True,
                'diseases': formatted_diseases,
                'source': 'memory'
            })
        
    except Exception as e:
        logger.error(f"Error fetching diseases: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/diseases/<disease_name>', methods=['GET'])
@login_required
def get_admin_disease(disease_name):
    """Get specific disease details (admin only)"""
    if current_user.user_type != 'admin':
        return jsonify({
            'success': False,
            'error': 'Unauthorized - Admin access required'
        }), 403
    
    try:
        # Try to get from database first
        if mongodb and mongodb.connected:
            disease = mongodb.get_disease(disease_name)
            
            if disease:
                disease_dict = {
                    '_id': str(disease['_id']),
                    'name': disease.get('name'),
                    'severity': disease.get('severity'),
                    'description': disease.get('description'),
                    'symptoms': disease.get('symptoms', []),
                    'causes': disease.get('causes', []),
                    'treatment': disease.get('treatment', []),
                    'prevention': disease.get('prevention', []),
                    'organic_solutions': disease.get('organic_solutions', []),
                    'created_at': disease['created_at'].isoformat() if disease.get('created_at') else None,
                    'updated_at': disease['updated_at'].isoformat() if disease.get('updated_at') else None
                }
                
                return jsonify({
                    'success': True,
                    'disease': disease_dict,
                    'source': 'database'
                })
        
        # Fallback to DISEASE_INFO
        if disease_name in DISEASE_INFO:
            return jsonify({
                'success': True,
                'disease': {
                    'name': disease_name,
                    **DISEASE_INFO[disease_name]
                },
                'source': 'memory'
            })
        
        return jsonify({
            'success': False,
            'error': 'Disease not found'
        }), 404
        
    except Exception as e:
        logger.error(f"Error fetching disease: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/diseases/<disease_name>', methods=['PUT'])
@login_required
def update_admin_disease(disease_name):
    """Update disease information (admin only)"""
    if current_user.user_type != 'admin':
        return jsonify({
            'success': False,
            'error': 'Unauthorized - Admin access required'
        }), 403
    
    if not (mongodb and mongodb.connected):
        return jsonify({
            'success': False,
            'error': 'MongoDB not configured - cannot save changes'
        }), 503
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['severity', 'description', 'symptoms', 'causes', 'treatment', 'organic_solutions']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Prepare disease data
        disease_data = {
            'name': disease_name,
            'severity': data['severity'],
            'description': data['description'],
            'symptoms': data['symptoms'] if isinstance(data['symptoms'], list) else [],
            'causes': data['causes'] if isinstance(data['causes'], list) else [],
            'treatment': data['treatment'] if isinstance(data['treatment'], list) else [],
            'prevention': data.get('prevention', []),
            'organic_solutions': data['organic_solutions'] if isinstance(data['organic_solutions'], list) else []
        }
        
        # Update in database
        success = mongodb.update_disease(disease_name, disease_data)
        
        if success:
            # Get updated disease
            updated_disease = mongodb.get_disease(disease_name)
            
            return jsonify({
                'success': True,
                'message': 'Disease updated successfully',
                'disease': {
                    '_id': str(updated_disease['_id']),
                    'name': updated_disease.get('name'),
                    'severity': updated_disease.get('severity'),
                    'description': updated_disease.get('description'),
                    'symptoms': updated_disease.get('symptoms', []),
                    'causes': updated_disease.get('causes', []),
                    'treatment': updated_disease.get('treatment', []),
                    'prevention': updated_disease.get('prevention', []),
                    'organic_solutions': updated_disease.get('organic_solutions', []),
                    'updated_at': updated_disease['updated_at'].isoformat() if updated_disease.get('updated_at') else None
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update disease'
            }), 500
        
    except Exception as e:
        logger.error(f"Error updating disease: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/locations', methods=['GET'])
@login_required
def get_location_statistics():
    """Get detailed location statistics (admin only)"""
    if current_user.user_type != 'admin':
        return jsonify({
            'success': False,
            'error': 'Unauthorized - Admin access required'
        }), 403
    
    if not (mongodb and mongodb.connected):
        return jsonify({
            'success': False,
            'error': 'MongoDB not configured'
        }), 503
    
    try:
        # Get location statistics from database
        locations = mongodb.get_location_statistics()
        
        return jsonify({
            'success': True,
            'total_locations': len(locations),
            'locations': locations
        })
        
    except Exception as e:
        logger.error(f"Error fetching location statistics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/messages', methods=['GET'])
@login_required
def get_all_messages():
    """Get all contact messages grouped by user (admin only)"""
    if current_user.user_type != 'admin':
        return jsonify({
            'success': False,
            'error': 'Unauthorized - Admin access required'
        }), 403
    
    if not (mongodb and mongodb.connected):
        return jsonify({
            'success': False,
            'error': 'MongoDB not configured'
        }), 503
    
    try:
        # Get all messages from contact_messages collection
        messages = list(mongodb.db.contact_messages.find().sort('timestamp', -1))
        
        # Group messages by user email
        user_conversations = {}
        for msg in messages:
            email = msg['email']
            if email not in user_conversations:
                # Initialize conversation with user's name (skip if this is an admin reply)
                user_name = msg['name'] if msg.get('type') != 'admin_reply' else 'User'
                user_conversations[email] = {
                    'email': email,
                    'name': user_name,
                    'messages': [],
                    'unread_count': 0,
                    'last_message_time': msg['timestamp']
                }
            
            # Update conversation name if we haven't found the user's real name yet
            # (in case the first message was an admin reply)
            if user_conversations[email]['name'] == 'User' and msg.get('type') != 'admin_reply':
                user_conversations[email]['name'] = msg['name']
            
            # Convert ObjectId to string
            msg['_id'] = str(msg['_id'])
            msg['timestamp'] = msg['timestamp'].isoformat() if msg.get('timestamp') else None
            
            # Count unread messages (only count user messages, not admin replies)
            if msg.get('status') == 'new' and msg.get('type') != 'admin_reply':
                user_conversations[email]['unread_count'] += 1
            
            user_conversations[email]['messages'].append(msg)
        
        # Convert to list and sort by last message time
        conversations_list = list(user_conversations.values())
        conversations_list.sort(key=lambda x: x['last_message_time'], reverse=True)
        
        # Format timestamps for sorting
        for conv in conversations_list:
            conv['last_message_time'] = conv['last_message_time'].isoformat() if conv.get('last_message_time') else None
        
        return jsonify({
            'success': True,
            'conversations': conversations_list,
            'total_conversations': len(conversations_list),
            'total_messages': len(messages)
        })
        
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/messages/<email>', methods=['GET'])
@login_required
def get_user_messages(email):
    """Get all messages for a specific user (admin only)"""
    if current_user.user_type != 'admin':
        return jsonify({
            'success': False,
            'error': 'Unauthorized - Admin access required'
        }), 403
    
    if not (mongodb and mongodb.connected):
        return jsonify({
            'success': False,
            'error': 'MongoDB not configured'
        }), 503
    
    try:
        # Get messages for this user
        messages = list(mongodb.db.contact_messages.find({'email': email}).sort('timestamp', 1))
        
        # Format messages
        for msg in messages:
            msg['_id'] = str(msg['_id'])
            msg['timestamp'] = msg['timestamp'].isoformat() if msg.get('timestamp') else None
        
        return jsonify({
            'success': True,
            'messages': messages,
            'email': email
        })
        
    except Exception as e:
        logger.error(f"Error fetching user messages: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/messages/<email>/reply', methods=['POST'])
@login_required
def reply_to_message(email):
    """Send a reply to a user message (admin only)"""
    if current_user.user_type != 'admin':
        return jsonify({
            'success': False,
            'error': 'Unauthorized - Admin access required'
        }), 403
    
    if not (mongodb and mongodb.connected):
        return jsonify({
            'success': False,
            'error': 'MongoDB not configured'
        }), 503
    
    try:
        data = request.get_json()
        reply_message = data.get('message', '').strip()
        
        if not reply_message:
            return jsonify({
                'success': False,
                'error': 'Reply message is required'
            }), 400
        
        # Store the reply in contact_messages collection
        # Use the user's email so the reply appears in their conversation
        reply_data = {
            'name': 'Admin',
            'email': email,  # User's email (so reply appears in their conversation)
            'admin_email': current_user.email,  # Track which admin replied
            'subject': 'Reply from Admin',
            'message': reply_message,
            'timestamp': datetime.now(),
            'status': 'replied',
            'type': 'admin_reply'
        }
        
        result = mongodb.db.contact_messages.insert_one(reply_data)
        
        # Send notification to the user
        notification_data = {
            'user_email': email,
            'title': 'Admin Reply',
            'message': f'The admin has replied to your message: {reply_message[:100]}...' if len(reply_message) > 100 else reply_message,
            'type': 'admin_reply',
            'created_at': datetime.now(),
            'read': False
        }
        mongodb.db.notifications.insert_one(notification_data)
        
        # Send email notification if email is configured
        try:
            if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
                msg = Message(
                    subject="Reply from Chilli Care Admin",
                    recipients=[email],
                    body=f"""
Hello,

The Chilli Care admin team has replied to your message:

{reply_message}

---
Chilli Care Admin Team
                    """.strip()
                )
                mail.send(msg)
                logger.info(f"Reply email sent to {email}")
        except Exception as email_error:
            logger.warning(f"Could not send email notification: {email_error}")
        
        return jsonify({
            'success': True,
            'message': 'Reply sent successfully',
            'reply_id': str(result.inserted_id)
        })
        
    except Exception as e:
        logger.error(f"Error sending reply: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/messages/<message_id>/mark-read', methods=['POST'])
@login_required
def mark_message_read(message_id):
    """Mark a message as read (admin only)"""
    if current_user.user_type != 'admin':
        return jsonify({
            'success': False,
            'error': 'Unauthorized - Admin access required'
        }), 403
    
    if not (mongodb and mongodb.connected):
        return jsonify({
            'success': False,
            'error': 'MongoDB not configured'
        }), 503
    
    try:
        from bson import ObjectId
        
        # Update message status
        result = mongodb.db.contact_messages.update_one(
            {'_id': ObjectId(message_id)},
            {'$set': {'status': 'read'}}
        )
        
        if result.modified_count > 0:
            return jsonify({
                'success': True,
                'message': 'Message marked as read'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Message not found or already read'
            }), 404
        
    except Exception as e:
        logger.error(f"Error marking message as read: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Load model at startup
    logger.info("Starting Chilli Disease Detection System...")
    load_model_and_classes()
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False,
        threaded=True
    )
