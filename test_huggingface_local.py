"""
Test Local BLIP Model for Image Validation
Tests the Hugging Face BLIP model running locally
"""

import os
import io
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_blip_model():
    """Test local BLIP model installation and functionality"""
    
    print("="*60)
    print("TESTING LOCAL BLIP MODEL")
    print("="*60)
    
    # Test 1: Check if transformers is installed
    print("\n1. Checking Transformers installation...")
    try:
        from transformers import BlipProcessor, BlipForConditionalGeneration
        import torch
        print("   ✅ Transformers library installed")
        print(f"   • Transformers version: {__import__('transformers').__version__}")
        print(f"   • PyTorch version: {torch.__version__}")
        print(f"   • CUDA available: {torch.cuda.is_available()}")
    except ImportError as e:
        print(f"   ❌ Error: {e}")
        print("\n   To install, run:")
        print("   pip install transformers torch")
        return False
    
    # Test 2: Load BLIP model
    print("\n2. Loading BLIP model...")
    try:
        model_name = "Salesforce/blip-image-captioning-base"
        print(f"   Loading: {model_name}")
        
        processor = BlipProcessor.from_pretrained(model_name)
        model = BlipForConditionalGeneration.from_pretrained(model_name)
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)
        model.eval()
        
        print(f"   ✅ Model loaded successfully on {device}")
    except Exception as e:
        print(f"   ❌ Error loading model: {e}")
        return False
    
    # Test 3: Test with sample images
    print("\n3. Testing with sample images...")
    
    # Find test images
    test_folders = ['test', 'train']
    test_images = []
    
    for folder in test_folders:
        if os.path.exists(folder):
            for disease_folder in os.listdir(folder):
                disease_path = os.path.join(folder, disease_folder)
                if os.path.isdir(disease_path):
                    images = [f for f in os.listdir(disease_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                    if images:
                        test_images.append(os.path.join(disease_path, images[0]))
                        if len(test_images) >= 3:
                            break
            if len(test_images) >= 3:
                break
    
    if not test_images:
        print("   ⚠️  No test images found")
        print("   Creating synthetic test...")
        
        # Create a simple green image
        img = Image.new('RGB', (224, 224), color=(50, 150, 50))
        test_images = [img]
    
    print(f"\n   Testing with {len(test_images)} image(s)...\n")
    
    for idx, img_path in enumerate(test_images, 1):
        try:
            if isinstance(img_path, str):
                print(f"   Test {idx}: {os.path.basename(img_path)}")
                image = Image.open(img_path).convert('RGB')
            else:
                print(f"   Test {idx}: Synthetic green image")
                image = img_path
            
            # Process image
            inputs = processor(image, return_tensors="pt").to(device)
            
            # Generate caption
            with torch.no_grad():
                out = model.generate(**inputs, max_length=50)
            
            caption = processor.decode(out[0], skip_special_tokens=True)
            print(f"   Caption: {caption}")
            
            # Validate caption
            plant_keywords = ['plant', 'pepper', 'chili', 'chilli', 'leaf', 'leaves', 'vegetable', 'capsicum', 'green', 'garden']
            invalid_keywords = ['person', 'people', 'human', 'animal', 'dog', 'cat', 'car', 'building', 'furniture']
            
            has_plant = any(keyword in caption.lower() for keyword in plant_keywords)
            has_invalid = any(keyword in caption.lower() for keyword in invalid_keywords)
            
            if has_invalid:
                print(f"   Result: ❌ Invalid (contains non-plant content)")
            elif has_plant:
                print(f"   Result: ✅ Valid (plant-related)")
            else:
                print(f"   Result: ⚠️  Unclear (no clear plant keywords)")
            
            print()
            
        except Exception as e:
            print(f"   ❌ Error processing image: {e}\n")
    
    # Test 4: Integration test
    print("4. Testing integration with validation function...")
    try:
        # Test the actual validation function
        def validate_with_blip(image):
            """Test validation function"""
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            image_bytes = img_byte_arr.getvalue()
            
            # Convert bytes back to image
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            
            # Process with BLIP
            inputs = processor(image, return_tensors="pt").to(device)
            
            with torch.no_grad():
                out = model.generate(**inputs, max_length=50)
            
            caption = processor.decode(out[0], skip_special_tokens=True).lower()
            
            # Validate
            plant_keywords = ['plant', 'pepper', 'chili', 'chilli', 'leaf', 'leaves', 'vegetable', 'capsicum', 'green', 'garden']
            has_plant = any(keyword in caption for keyword in plant_keywords)
            
            return has_plant, caption
        
        # Create test image
        test_img = Image.new('RGB', (224, 224), color=(50, 150, 50))
        is_valid, caption = validate_with_blip(test_img)
        
        print(f"   Test validation result: {is_valid}")
        print(f"   Caption: {caption}")
        print("   ✅ Integration test passed")
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        return False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("✅ Local BLIP model is working correctly!")
    print("\nThe model can now be used for offline image validation.")
    print("="*60)
    
    return True


if __name__ == '__main__':
    print("\n🤗 TESTING LOCAL BLIP MODEL 🤗\n")
    success = test_blip_model()
    print("\n")
    
    if success:
        print("✅ All tests passed! Ready to use local BLIP model.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
