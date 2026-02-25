"""
MongoDB Database Initialization Script
Populates the database with disease information
"""

import os
from dotenv import load_dotenv
from mongodb_database import MongoDB

# Load environment variables
load_dotenv()

# Disease information to populate
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


def init_mongodb():
    """Initialize MongoDB with disease data"""
    
    print("="*60)
    print("CHILLI DISEASE DETECTION - MONGODB INITIALIZATION")
    print("="*60)
    
    # Check for MongoDB URI
    mongodb_uri = os.getenv('MONGODB_URI', '')
    
    if not mongodb_uri:
        print("\n❌ ERROR: MONGODB_URI not found in environment variables!")
        print("\nPlease add your MongoDB connection string to .env file:")
        print("MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/chilli_care")
        return False
    
    print(f"\nConnecting to MongoDB...")
    print(f"URI: {mongodb_uri[:30]}...{mongodb_uri[-20:]}")
    
    # Create MongoDB instance
    db = MongoDB(mongodb_uri)
    
    if not db.connected:
        print("\n❌ Failed to connect to MongoDB!")
        print("Please check your connection string and network connection.")
        return False
    
    print("✅ Connected to MongoDB successfully!")
    
    # Check existing data
    existing_diseases = db.get_all_diseases()
    
    if existing_diseases:
        print(f"\n⚠️  Database already contains {len(existing_diseases)} disease(s).")
        response = input("Do you want to recreate the disease data? (yes/no): ")
        
        if response.lower() != 'yes':
            print("❌ Aborted. Existing data preserved.")
            db.close()
            return False
        
        # Clear existing diseases
        db.db.diseases.delete_many({})
        print("✅ Cleared existing disease data.")
    
    # Populate disease information
    print("\n📝 Populating disease information...")
    
    for disease_name, disease_data in DISEASE_INFO.items():
        # Add name to the data
        disease_data['name'] = disease_name
        
        result = db.insert_disease(disease_data)
        
        if result:
            print(f"  ✓ Added: {disease_name}")
        else:
            print(f"  ✗ Failed: {disease_name}")
    
    # Display summary
    print("\n" + "="*60)
    print("DATABASE SUMMARY")
    print("="*60)
    
    total_diseases = db.db.diseases.count_documents({})
    total_predictions = db.db.predictions.count_documents({})
    
    print(f"Total Diseases: {total_diseases}")
    print(f"Total Predictions: {total_predictions}")
    print("="*60)
    
    # Display all diseases
    print("\nDiseases in database:")
    for disease in db.get_all_diseases():
        print(f"  • {disease['name']} (Severity: {disease['severity']})")
    
    print("\n✅ MongoDB initialization complete!")
    
    db.close()
    return True


if __name__ == '__main__':
    try:
        init_mongodb()
    except Exception as e:
        print(f"\n❌ Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()
