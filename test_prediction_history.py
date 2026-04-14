"""
Test Prediction History Page Functionality
This script tests all functionalities of the prediction history page
"""

import requests
import json
import sys
from datetime import datetime

# Base URL
BASE_URL = "http://localhost:5000"

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def test_api_endpoint(endpoint, method="GET", data=None, description=""):
    """Test an API endpoint"""
    print(f"\n🔍 Testing: {description}")
    print(f"   Endpoint: {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   ✅ Success: {json.dumps(result, indent=2)[:200]}...")
                return True, result
            except:
                print(f"   ✅ Success (non-JSON response)")
                return True, response.text
        else:
            print(f"   ❌ Failed: {response.text[:200]}")
            return False, None
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False, None

def main():
    print_header("PREDICTION HISTORY FUNCTIONALITY TEST")
    print(f"Testing URL: {BASE_URL}")
    print(f"Test Time: {datetime.now()}")
    
    results = {'passed': 0, 'failed': 0, 'total': 0}
    
    # Test 1: Check server is running
    print_header("1. SERVER CONNECTIVITY")
    success, _ = test_api_endpoint("/", description="Home page accessibility")
    results['total'] += 1
    if success:
        results['passed'] += 1
    else:
        results['failed'] += 1
        print("\n⚠️  Server not running. Please start the Flask application first.")
        print("   Run: python app.py")
        return
    
    # Test 2: Check MongoDB connection
    print_header("2. DATABASE CONNECTION")
    success, data = test_api_endpoint("/api/history?page=1&per_page=5", 
                                     description="MongoDB connection via /api/history")
    results['total'] += 1
    if success:
        results['passed'] += 1
        if data and data.get('success'):
            print(f"   📊 Total predictions in DB: {data.get('total', 0)}")
            print(f"   📄 Predictions per page: {data.get('per_page', 0)}")
            print(f"   📚 Total pages: {data.get('pages', 0)}")
        else:
            print(f"   ⚠️  API returned success=False: {data.get('error', 'Unknown error')}")
    else:
        results['failed'] += 1
        print("   ⚠️  MongoDB may not be configured or connected")
    
    # Test 3: Check admin predictions endpoint (requires authentication)
    print_header("3. ADMIN PREDICTIONS ENDPOINT")
    success, data = test_api_endpoint("/api/admin/predictions?page=1&limit=5",
                                     description="Admin predictions with filters")
    results['total'] += 1
    if success:
        results['passed'] += 1
        if data and data.get('success'):
            print(f"   📊 Statistics:")
            stats = data.get('statistics', {})
            print(f"      - Total predictions: {stats.get('total_predictions', 0)}")
            print(f"      - Average confidence: {stats.get('avg_confidence', 0)}%")
            print(f"      - Healthy count: {stats.get('healthy_count', 0)}")
            print(f"      - Diseased count: {stats.get('diseased_count', 0)}")
        else:
            print(f"   ⚠️  Requires admin authentication")
    else:
        results['failed'] += 1
        print("   ⚠️  This endpoint requires admin login")
    
    # Test 4: Test disease filter
    print_header("4. DISEASE FILTER FUNCTIONALITY")
    success, data = test_api_endpoint("/api/history?disease=Chilli___healthy&page=1",
                                     description="Filter by disease (Healthy)")
    results['total'] += 1
    if success and data and data.get('success'):
        results['passed'] += 1
        print(f"   ✅ Filtered results: {len(data.get('predictions', []))} predictions")
        print(f"   📊 Total healthy predictions: {data.get('total', 0)}")
    else:
        results['failed'] += 1
    
    # Test 5: Test pagination
    print_header("5. PAGINATION FUNCTIONALITY")
    success1, data1 = test_api_endpoint("/api/history?page=1&per_page=5",
                                       description="Page 1 (5 per page)")
    success2, data2 = test_api_endpoint("/api/history?page=2&per_page=5",
                                       description="Page 2 (5 per page)")
    results['total'] += 1
    if success1 and success2:
        results['passed'] += 1
        print(f"   ✅ Pagination working")
        if data1 and data2:
            print(f"   📄 Page 1: {len(data1.get('predictions', []))} results")
            print(f"   📄 Page 2: {len(data2.get('predictions', []))} results")
    else:
        results['failed'] += 1
    
    # Test 6: Check if prediction data has required fields
    print_header("6. PREDICTION DATA STRUCTURE")
    success, data = test_api_endpoint("/api/history?page=1&per_page=1",
                                     description="Check prediction fields")
    results['total'] += 1
    if success and data and data.get('predictions') and len(data['predictions']) > 0:
        pred = data['predictions'][0]
        required_fields = ['_id', 'timestamp', 'predicted_disease', 'confidence']
        missing_fields = [f for f in required_fields if f not in pred]
        
        if not missing_fields:
            results['passed'] += 1
            print(f"   ✅ All required fields present:")
            print(f"      - ID: {pred.get('_id', 'N/A')}")
            print(f"      - Disease: {pred.get('predicted_disease', 'N/A')}")
            print(f"      - Confidence: {pred.get('confidence', 'N/A')}%")
            print(f"      - Timestamp: {pred.get('timestamp', 'N/A')}")
            if 'user_email' in pred:
                print(f"      - User: {pred.get('user_email', 'N/A')}")
            if 'location' in pred:
                print(f"      - Location: {pred.get('location', 'N/A')}")
        else:
            results['failed'] += 1
            print(f"   ❌ Missing fields: {', '.join(missing_fields)}")
    else:
        results['failed'] += 1
        print(f"   ⚠️  No predictions available to test")
    
    # Test 7: Frontend JavaScript file exists
    print_header("7. FRONTEND FILES")
    import os
    js_file = "static/js/admin_dashboard.js"
    if os.path.exists(js_file):
        print(f"   ✅ {js_file} exists")
        # Check if key functions exist
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            functions = [
                'loadPredictions',
                'displayPredictions',
                'updatePredictionStatistics',
                'initPredictionManagement'
            ]
            missing = []
            for func in functions:
                if func not in content:
                    missing.append(func)
            
            if not missing:
                print(f"   ✅ All key functions present")
                results['passed'] += 1
            else:
                print(f"   ❌ Missing functions: {', '.join(missing)}")
                results['failed'] += 1
    else:
        print(f"   ❌ {js_file} not found")
        results['failed'] += 1
    results['total'] += 1
    
    # Summary
    print_header("TEST SUMMARY")
    print(f"   Total Tests: {results['total']}")
    print(f"   ✅ Passed: {results['passed']}")
    print(f"   ❌ Failed: {results['failed']}")
    print(f"   Success Rate: {(results['passed']/results['total']*100):.1f}%")
    
    if results['failed'] == 0:
        print("\n🎉 All tests passed! Prediction history functionality is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
