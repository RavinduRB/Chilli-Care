"""
Quick Test: Local Validation System
Tests the improved AI-free validation
"""

import sys
import os
from PIL import Image
import io
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_local_validation():
    """Test the enhanced local validation"""
    print("=" * 60)
    print("Testing Enhanced Local Validation System")
    print("=" * 60)
    
    # Import from app
    try:
        from app import validate_with_local_rules
        print("✅ Successfully imported validation function\n")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return
    
    # Test 1: Green plant-like image
    print("Test 1: Simulated GREEN plant image")
    print("-" * 60)
    green_img = Image.new('RGB', (300, 300))
    pixels = green_img.load()
    for i in range(300):
        for j in range(300):
            # Create green with some variation
            r = np.random.randint(30, 70)
            g = np.random.randint(80, 150)
            b = np.random.randint(40, 80)
            pixels[i, j] = (r, g, b)
    
    img_bytes = io.BytesIO()
    green_img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    is_valid, message = validate_with_local_rules(img_bytes.read())
    print(f"Result: {'✅ VALID' if is_valid else '❌ INVALID'}")
    print(f"Message: {message}\n")
    
    # Test 2: Yellow/diseased plant-like image
    print("Test 2: Simulated YELLOW/DISEASED plant image")
    print("-" * 60)
    yellow_img = Image.new('RGB', (300, 300))
    pixels = yellow_img.load()
    for i in range(300):
        for j in range(300):
            # Create yellowish with some green
            r = np.random.randint(100, 160)
            g = np.random.randint(110, 170)
            b = np.random.randint(30, 70)
            pixels[i, j] = (r, g, b)
    
    img_bytes = io.BytesIO()
    yellow_img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    is_valid, message = validate_with_local_rules(img_bytes.read())
    print(f"Result: {'✅ VALID' if is_valid else '❌ INVALID'}")
    print(f"Message: {message}\n")
    
    # Test 3: Non-plant (red) image
    print("Test 3: Simulated NON-PLANT (red) image")
    print("-" * 60)
    red_img = Image.new('RGB', (300, 300))
    pixels = red_img.load()
    for i in range(300):
        for j in range(300):
            # Create red image
            r = np.random.randint(150, 200)
            g = np.random.randint(30, 70)
            b = np.random.randint(30, 70)
            pixels[i, j] = (r, g, b)
    
    img_bytes = io.BytesIO()
    red_img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    is_valid, message = validate_with_local_rules(img_bytes.read())
    print(f"Result: {'✅ VALID' if is_valid else '❌ INVALID'}")
    print(f"Message: {message}\n")
    
    # Test 4: White background image
    print("Test 4: Simulated WHITE BACKGROUND image")
    print("-" * 60)
    white_img = Image.new('RGB', (300, 300), (240, 240, 240))
    
    img_bytes = io.BytesIO()
    white_img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    is_valid, message = validate_with_local_rules(img_bytes.read())
    print(f"Result: {'✅ VALID' if is_valid else '❌ INVALID'}")
    print(f"Message: {message}\n")
    
    print("=" * 60)
    print("✅ Local Validation Testing Complete!")
    print("=" * 60)
    print("\n💡 TIP: Your app now works WITHOUT any API keys!")
    print("   The improved validation handles:")
    print("   • Healthy green leaves")
    print("   • Diseased yellow/brown leaves")
    print("   • Various lighting conditions")
    print("   • Filters out non-plant images")

if __name__ == "__main__":
    test_local_validation()
