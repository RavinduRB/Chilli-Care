"""
ChilliDoc AI - API Test Script
Tests all API endpoints and functionality
"""

import requests
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.END}")

# Test 1: Health Check
def test_health_check():
    print_header("Test 1: Health Check")
    try:
        response = requests.get(f"{API_URL}/health")
        data = response.json()
        
        if response.status_code == 200:
            print_success("Health check endpoint working")
            print(f"   Status: {data['status']}")
            print(f"   Model loaded: {data['model_loaded']}")
            print(f"   Classes: {data['num_classes']}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False

# Test 2: Get All Diseases
def test_get_diseases():
    print_header("Test 2: Get All Diseases")
    try:
        response = requests.get(f"{API_URL}/diseases")
        data = response.json()
        
        if response.status_code == 200 and data['success']:
            print_success(f"Retrieved {data['total_diseases']} diseases")
            for disease_name in data['diseases'].keys():
                print(f"   - {disease_name}")
            return True
        else:
            print_error("Failed to get diseases list")
            return False
    except Exception as e:
        print_error(f"Get diseases error: {str(e)}")
        return False

# Test 3: Get Specific Disease
def test_get_disease_info():
    print_header("Test 3: Get Specific Disease Info")
    disease_name = "Chilli Anthacnose"
    
    try:
        response = requests.get(f"{API_URL}/disease/{disease_name}")
        data = response.json()
        
        if response.status_code == 200 and data['success']:
            print_success(f"Retrieved info for: {disease_name}")
            info = data['info']
            print(f"   Severity: {info['severity']}")
            print(f"   Symptoms: {len(info['symptoms'])} listed")
            print(f"   Treatments: {len(info['treatment'])} listed")
            return True
        else:
            print_error(f"Failed to get disease info")
            return False
    except Exception as e:
        print_error(f"Get disease info error: {str(e)}")
        return False

# Test 4: Predict Disease
def test_predict_disease():
    print_header("Test 4: Predict Disease from Image")
    
    # Find a test image - prioritize healthy images as they're more likely to pass validation
    test_dirs_priority = [
        ('test/Chilli___healthy', 'Healthy chilli'),
        ('test/Chilli__Anthacnose', 'Anthacnose'),
        ('test/Chilli__Leaf_Curl_Virus', 'Leaf Curl Virus'),
        ('test/Chilli __Yellowish', 'Yellowish'),
        ('test/Chilli __Whitefly', 'Whitefly'),
        ('valid/Chilli___healthy', 'Healthy chilli'),
        ('train/Chilli___healthy', 'Healthy chilli')
    ]
    
    test_image_path = None
    
    for test_dir, category in test_dirs_priority:
        if os.path.exists(test_dir):
            images = [f for f in os.listdir(test_dir) 
                     if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if images:
                # Try the first image from this directory
                test_image_path = os.path.join(test_dir, images[0])
                print_info(f"Using test image from {category}: {test_image_path}")
                break
    
    if not test_image_path:
        print_error("No test image found")
        print_info("Please ensure you have images in train/valid/test directories")
        return False
    
    try:
        with open(test_image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{API_URL}/predict", files=files)
            data = response.json()
        
        if response.status_code == 200 and data['success']:
            print_success("Prediction successful!")
            
            prediction = data['prediction']
            print(f"\n   Disease: {prediction['predicted_class']}")
            print(f"   Confidence: {prediction['confidence']:.2f}%")
            
            print(f"\n   Top 3 Predictions:")
            for i, (disease, prob) in enumerate(prediction['top_3_predictions'], 1):
                print(f"      {i}. {disease}: {prob:.2f}%")
            
            disease_info = data['disease_info']
            print(f"\n   Severity: {disease_info['severity']}")
            print(f"   Treatment options: {len(disease_info['treatment'])}")
            
            return True
        else:
            error_msg = data.get('error', 'Unknown error')
            detail_msg = data.get('message', '')
            print_error(f"Prediction failed: {error_msg}")
            if detail_msg:
                print_info(f"Details: {detail_msg}")
            return False
    except Exception as e:
        print_error(f"Prediction error: {str(e)}")
        return False

# Test 5: Invalid Endpoint
def test_invalid_endpoint():
    print_header("Test 5: Invalid Endpoint (Error Handling)")
    try:
        response = requests.get(f"{API_URL}/invalid-endpoint")
        
        if response.status_code == 404:
            print_success("404 error handled correctly")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Invalid endpoint test error: {str(e)}")
        return False

# Test 6: Invalid File Upload
def test_invalid_file():
    print_header("Test 6: Invalid File Upload (Validation)")
    
    # Create a dummy text file
    test_file_path = "test_invalid.txt"
    with open(test_file_path, 'w') as f:
        f.write("This is not an image")
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{API_URL}/predict", files=files)
            data = response.json()
        
        # Clean up
        os.remove(test_file_path)
        
        if response.status_code == 400:
            print_success("Invalid file type rejected correctly")
            print(f"   Error message: {data.get('error', 'N/A')}")
            return True
        else:
            print_error(f"Unexpected behavior: {response.status_code}")
            return False
    except Exception as e:
        # Clean up on error
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        print_error(f"Invalid file test error: {str(e)}")
        return False

# Run all tests
def run_all_tests():
    print_header("ChilliDoc AI - API Test Suite")
    print_info(f"Testing API at: {BASE_URL}")
    
    tests = [
        ("Health Check", test_health_check),
        ("Get All Diseases", test_get_diseases),
        ("Get Disease Info", test_get_disease_info),
        ("Predict Disease", test_predict_disease),
        ("Invalid Endpoint", test_invalid_endpoint),
        ("Invalid File Upload", test_invalid_file),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print_header("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{status}{Colors.END} - {test_name}")
    
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  Results: {passed}/{total} tests passed")
    if passed == total:
        print(f"  🎉 All tests passed! API is working correctly.")
    elif passed > 0:
        print(f"  ⚠️  Some tests failed. Check the output above.")
    else:
        print(f"  ❌ All tests failed. Is the server running?")
    print(f"{'='*60}{Colors.END}\n")
    
    return passed == total

if __name__ == "__main__":
    print("\n")
    print("=" * 60)
    print("   ChilliDoc AI - Automated API Testing")
    print("=" * 60)
    print("\nMake sure the server is running at http://localhost:5000")
    print("Run: python app.py")
    print("\nPress Enter to start tests or Ctrl+C to cancel...")
    input()
    
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests cancelled by user.")
        exit(1)
