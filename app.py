"""
Chilli Disease Detection - Industry-Level Web Application
Modern Flask API with TensorFlow Model Integration
"""

import os
import json
import numpy as np
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
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

# Load environment variables from .env file
load_dotenv()

# Configure logging (must be before MongoDB import that uses logger)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import MongoDB database
try:
    from mongodb_database import get_db
    mongodb = get_db()
    logger.info(f"✓ MongoDB configured: {mongodb.connected}")
except ImportError as e:
    logger.warning(f"⚠ MongoDB not available: {e}")
    mongodb = None

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
CORS(app)  # Enable CORS for API access

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure Multiple Gemini API Keys for Rotation
GEMINI_API_KEYS = [
    os.environ.get('GEMINI_API_KEY', ''),
    os.environ.get('GEMINI_API_KEY_2', ''),
    os.environ.get('GEMINI_API_KEY_3', ''),
    os.environ.get('GEMINI_API_KEY_4', ''),
    os.environ.get('GEMINI_API_KEY_5', ''),
]
# Remove empty keys
GEMINI_API_KEYS = [key for key in GEMINI_API_KEYS if key]

# Configure Hugging Face API as backup
HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY', '')

if GEMINI_API_KEYS:
    logger.info(f"✓ Configured {len(GEMINI_API_KEYS)} Gemini API key(s)")
else:
    logger.warning("⚠ No Gemini API keys set")

if HUGGINGFACE_API_KEY:
    logger.info("✓ Hugging Face API configured as backup")

# Current API key index for rotation
current_gemini_key_index = 0

# Global variables for model and settings
model = None
class_names = []
IMG_HEIGHT = 224
IMG_WIDTH = 224

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
    Use Hugging Face API as backup validation
    Free tier with rate limiting
    """
    try:
        if not HUGGINGFACE_API_KEY:
            return None
        
        logger.info("🤗 Trying Hugging Face Vision API...")
        
        # Use Salesforce BLIP model for image captioning
        API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        
        response = requests.post(API_URL, headers=headers, data=image_bytes, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            caption = result[0]['generated_text'].lower() if isinstance(result, list) else result.get('generated_text', '').lower()
            
            logger.info(f"HuggingFace caption: {caption}")
            
            # Check if caption mentions plant, pepper, chilli, leaf, vegetable
            plant_keywords = ['plant', 'pepper', 'chili', 'chilli', 'leaf', 'leaves', 'vegetable', 'capsicum', 'green', 'garden']
            invalid_keywords = ['person', 'people', 'human', 'animal', 'dog', 'cat', 'car', 'building', 'furniture']
            
            has_plant = any(keyword in caption for keyword in plant_keywords)
            has_invalid = any(keyword in caption for keyword in invalid_keywords)
            
            if has_invalid:
                return False, f"Image appears to be: {caption}"
            elif has_plant:
                return True, "Image validated (HuggingFace backup)"
            else:
                return False, f"Unclear image content: {caption}"
        else:
            logger.warning(f"HuggingFace API error: {response.status_code}")
            return None
            
    except Exception as e:
        logger.warning(f"HuggingFace validation failed: {str(e)}")
        return None


def validate_with_local_rules(image_bytes):
    """
    Simple local validation using color analysis
    Ultimate fallback when all APIs are exhausted
    """
    try:
        logger.info("🔍 Using local color-based validation...")
        
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        # Resize for faster processing
        img.thumbnail((200, 200))
        
        pixels = list(img.getdata())
        total_pixels = len(pixels)
        
        # Count green pixels (likely plant)
        green_pixels = 0
        for r, g, b in pixels:
            # Green dominant or greenish
            if g > r and g > b and g > 50:
                green_pixels += 1
        
        green_ratio = green_pixels / total_pixels
        
        logger.info(f"Green pixel ratio: {green_ratio:.2%}")
        
        # If >15% green pixels, likely a plant
        if green_ratio > 0.15:
            return True, "Image contains plant-like colors (local validation)"
        else:
            return False, "Image doesn't appear to contain plant leaves"
            
    except Exception as e:
        logger.error(f"Local validation failed: {str(e)}")
        # When everything fails, allow through
        return True, "Validation unavailable"


def validate_chilli_image(image_file):
    """
    Multi-tier validation system with automatic fallback:
    1. Try all Gemini API keys (rotate through multiple accounts)
    2. Try Hugging Face API (free backup service)
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
        
        # === TIER 2: Try Hugging Face ===
        hf_result = validate_with_huggingface(image_bytes)
        if hf_result is not None:
            logger.info("✅ HuggingFace validation succeeded")
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
            'model_version': '1.0.0',
            'timestamp': datetime.utcnow()
        }
        
        prediction_id = mongodb.save_prediction(prediction_data)
        return prediction_id
        
    except Exception as e:
        logger.error(f"Failed to save prediction to MongoDB: {e}")
        return None


# Routes
@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/predict', methods=['POST'])
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
        
        # Save prediction to MongoDB
        user_ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')[:500]
        prediction_id = save_prediction_to_mongo(
            prediction_result,
            validation_message.split('(')[1].rstrip(')') if '(' in validation_message else 'unknown',
            validation_message,
            file.filename,
            user_ip,
            user_agent
        )
        
        # Prepare response
        response = {
            'success': True,
            'prediction': prediction_result,
            'disease_info': disease_data,
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
    if mongodb:
        mongodb_status = 'connected' if mongodb.connected else 'disconnected'
    
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'classes_loaded': len(class_names) > 0,
        'num_classes': len(class_names),
        'mongodb': mongodb_status,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


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
