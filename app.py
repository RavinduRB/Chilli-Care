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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
CORS(app)  # Enable CORS for API access

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
        
        # Preprocess image
        img_array, original_img = preprocess_image(file)
        
        # Make prediction
        prediction_result = predict_disease(img_array)
        
        # Get disease information
        disease_name = prediction_result['predicted_class']
        disease_data = DISEASE_INFO.get(disease_name, {})
        
        # Prepare response
        response = {
            'success': True,
            'prediction': prediction_result,
            'disease_info': disease_data,
            'timestamp': datetime.now().isoformat(),
            'model_version': '1.0.0'
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
    return jsonify({
        'success': True,
        'diseases': DISEASE_INFO,
        'total_diseases': len(DISEASE_INFO)
    })


@app.route('/api/disease/<disease_name>', methods=['GET'])
def get_disease_info(disease_name):
    """Get specific disease information"""
    disease_data = DISEASE_INFO.get(disease_name)
    
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
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'classes_loaded': len(class_names) > 0,
        'num_classes': len(class_names),
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
