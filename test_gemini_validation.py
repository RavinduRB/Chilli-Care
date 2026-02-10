"""
Test script for Gemini API image validation feature
This script demonstrates how the validation works
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
import io

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

def test_gemini_connection():
    """Test if Gemini API is properly configured"""
    print("🔍 Testing Gemini API Connection...")
    print(f"API Key Set: {'Yes ✓' if GEMINI_API_KEY else 'No ✗'}")
    
    if not GEMINI_API_KEY:
        print("\n⚠️  GEMINI_API_KEY not found!")
        print("Please set your API key:")
        print("1. Create a .env file in the project root")
        print("2. Add: GEMINI_API_KEY=your_api_key_here")
        print("3. Get your key from: https://makersuite.google.com/app/apikey")
        return False
    
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Try different models in order of preference
        # Prioritizing accuracy for image validation
        # Auto-switches if quota is exhausted
        model_names = [
            # Highest Accuracy models
            'models/gemini-3-pro-image-preview',
            'models/gemini-3-pro-preview',
            'models/gemini-2.5-pro',
            # Image-specialized
            'models/gemini-2.5-flash-image',
            'models/gemini-pro-latest',
            # Fast models
            'models/gemini-2.5-flash',
            'models/gemini-3-flash-preview',
            'models/gemini-2.0-flash',
            'models/gemini-flash-latest',
            # Experimental
            'models/gemini-exp-1206',
            # Flash variants
            'models/gemini-2.0-flash-001',
            'models/gemini-2.0-flash-lite',
            'models/gemini-2.5-flash-lite',
            'models/gemini-2.0-flash-lite-001',
            'models/gemini-flash-lite-latest',
            # Preview models
            'models/gemini-2.5-flash-preview-09-2025',
            'models/gemini-2.5-flash-lite-preview-09-2025',
        ]
        
        working_model = None
        for model_name in model_names:
            try:
                print(f"  Trying {model_name}...", end=' ')
                response = client.models.generate_content(
                    model=model_name,
                    contents="Say 'Hello' if you're working"
                )
                print(f"✓")
                working_model = model_name
                break
            except Exception as e:
                error_msg = str(e)
                if '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg:
                    print(f"✗ (Quota exhausted)")
                else:
                    print(f"✗ ({error_msg[:50]})")
                continue
        
        if working_model:
            print(f"\n✓ Connection successful!")
            print(f"✓ Working model: {working_model}")
            print(f"Response: {response.text}")
            return True
        else:
            print(f"\n✗ All models failed!")
            return False
        
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
        return False

def validate_chilli_image_test(image_path):
    """Test image validation with a sample image"""
    if not GEMINI_API_KEY:
        print("⚠️  Cannot test validation - API key not set")
        return
    
    if not os.path.exists(image_path):
        print(f"⚠️  Image not found: {image_path}")
        return
    
    print(f"\n📸 Testing image: {image_path}")
    
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Try to find a working model
        # Prioritizing accuracy
        model_names = [
            # Highest Accuracy
            'models/gemini-3-pro-image-preview',
            'models/gemini-3-pro-preview',
            'models/gemini-2.5-pro',
            # Image-specialized
            'models/gemini-2.5-flash-image',
            'models/gemini-pro-latest',
            # Fast models
            'models/gemini-2.5-flash',
            'models/gemini-3-flash-preview',
            'models/gemini-2.0-flash',
            'models/gemini-flash-latest',
            # Experimental
            'models/gemini-exp-1206',
            # Flash variants
            'models/gemini-2.0-flash-001',
            'models/gemini-2.0-flash-lite',
            'models/gemini-2.5-flash-lite',
            'models/gemini-2.0-flash-lite-001',
            'models/gemini-flash-lite-latest',
            # Preview models
            'models/gemini-2.5-flash-preview-09-2025',
            'models/gemini-2.5-flash-lite-preview-09-2025',
        ]
        
        working_model = None
        for model_name in model_names:
            try:
                print(f"  Trying {model_name}...", end=' ')
                # Test the model with a simple text prompt first
                test = client.models.generate_content(
                    model=model_name,
                    contents="Hi"
                )
                print(f"✓")
                working_model = model_name
                print(f"Using model: {model_name}")
                break
            except Exception as e:
                print(f"✗ ({str(e)[:40]})")
                continue
        
        if not working_model:
            print("❌ No working model found!")
            return None
        
        img = Image.open(image_path)
        
        # Convert image to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        image_bytes = img_byte_arr.read()
        
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
        
        response = client.models.generate_content(
            model=working_model,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
                prompt
            ]
        )
        result = response.text.strip()
        
        print(f"🤖 Gemini Response: {result}")
        
        if result.upper().startswith("VALID"):
            print("✅ Image is VALID - Chilli plant detected!")
        else:
            print("❌ Image is INVALID - Not a chilli plant")
        
        return result
        
    except Exception as e:
        print(f"Error during validation: {str(e)}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("🌶️  Chilli Disease Detection - Gemini Validation Test")
    print("=" * 60)
    
    # Test connection
    if test_gemini_connection():
        print("\n" + "=" * 60)
        print("📝 You can now test with actual images!")
        print("=" * 60)
        
        # Example: Test with images from test folder if they exist
        test_folders = [
            "test/Chilli___healthy/",
            "test/Chilli__Anthacnose/",
            "test/Chilli__Leaf_Curl_Virus/"
        ]
        
        found_images = False
        for folder in test_folders:
            if os.path.exists(folder):
                images = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                if images:
                    found_images = True
                    # Test first image in folder
                    test_image = os.path.join(folder, images[0])
                    validate_chilli_image_test(test_image)
                    break
        
        if not found_images:
            print("\n💡 No test images found. Place chilli images in test/ folders to test validation.")
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("=" * 60)
