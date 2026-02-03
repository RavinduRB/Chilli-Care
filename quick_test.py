"""
Quick API Test - Tests if the ChilliDoc AI API is working
"""

import requests
import os
import sys

BASE_URL = "http://localhost:5000"

print("\n" + "="*60)
print("   ChilliDoc AI - Quick API Test")
print("="*60 + "\n")

# Test 1: Server is running
print("1. Checking if server is running...")
try:
    response = requests.get(BASE_URL, timeout=5)
    if response.status_code == 200:
        print("   ✓ Server is running\n")
    else:
        print(f"   ✗ Server returned status {response.status_code}\n")
        sys.exit(1)
except requests.exceptions.ConnectionError:
    print("   ✗ Cannot connect to server!")
    print("   → Make sure the server is running: python app.py\n")
    sys.exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}\n")
    sys.exit(1)

# Test 2: Health check
print("2. Testing health endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/health")
    data = response.json()
    if data.get('status') == 'healthy':
        print(f"   ✓ API is healthy")
        print(f"   ✓ Model loaded: {data.get('model_loaded', False)}")
        print(f"   ✓ Classes loaded: {data.get('num_classes', 0)}\n")
    else:
        print("   ✗ API health check failed\n")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}\n")
    sys.exit(1)

# Test 3: Prediction with an actual image
print("3. Testing disease prediction...")
test_image = None

# Find a test image
for root, dirs, files in os.walk("test"):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            test_image = os.path.join(root, file)
            break
    if test_image:
        break

if not test_image:
    print("   ⚠ No test images found, skipping prediction test\n")
else:
    print(f"   Using: {os.path.basename(test_image)}")
    try:
        with open(test_image, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/api/predict", files=files)
            data = response.json()
        
        if data.get('success'):
            pred = data['prediction']
            print(f"   ✓ Prediction successful!")
            print(f"   → Disease: {pred['predicted_class']}")
            print(f"   → Confidence: {pred['confidence']:.2f}%\n")
        else:
            print(f"   ✗ Prediction failed: {data.get('error', 'Unknown error')}\n")
            print(f"   Full response: {data}\n")
            sys.exit(1)
    except Exception as e:
        print(f"   ✗ Error during prediction: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

print("="*60)
print("   ✓ All tests passed! API is working correctly!")
print("="*60 + "\n")
print(f"Open in browser: {BASE_URL}")
print()
