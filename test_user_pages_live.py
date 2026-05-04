"""
Functional test for all user-facing pages - Tests actual HTTP responses
"""
import requests
import time

BASE_URL = "http://localhost:5000"

def test_page(url, page_name):
    """Test if a page loads successfully"""
    try:
        full_url = f"{BASE_URL}{url}"
        response = requests.get(full_url, timeout=5)
        
        if response.status_code == 200:
            print(f"✓ {page_name}: Status 200 OK")
            return True
        else:
            print(f"✗ {page_name}: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ {page_name}: Error - {str(e)}")
        return False

def test_api(url, method='GET', page_name=''):
    """Test if an API endpoint responds"""
    try:
        full_url = f"{BASE_URL}{url}"
        
        if method == 'GET':
            response = requests.get(full_url, timeout=5)
        elif method == 'POST':
            response = requests.post(full_url, json={}, timeout=5)
        
        # Most APIs should return 200, 401, or 400 (not 404 or 500)
        if response.status_code in [200, 400, 401]:
            print(f"✓ {page_name}: Endpoint exists (Status {response.status_code})")
            return True
        else:
            print(f"✗ {page_name}: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ {page_name}: Error - {str(e)}")
        return False

def main():
    print("=" * 70)
    print("CHILLI CARE - LIVE FUNCTIONAL TEST FOR USER PAGES")
    print("=" * 70)
    print(f"\nTesting server at: {BASE_URL}")
    print("Make sure the Flask app is running!\n")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        if response.status_code == 200:
            print("✓ Server is running\n")
        else:
            print("⚠ Server responded but health check failed\n")
    except:
        print("✗ ERROR: Server is not running!")
        print("Please start the Flask app with: python app.py\n")
        return False
    
    # Test main pages
    print("=" * 70)
    print("TESTING: Main Navigation Pages")
    print("=" * 70)
    
    pages = [
        ('/', 'Home Page'),
        ('/about', 'About Page'),
        ('/diseases', 'Diseases Page'),
        ('/contact', 'Contact Page'),
        ('/analytics', 'Analytics Page')
    ]
    
    page_results = []
    for url, name in pages:
        result = test_page(url, name)
        page_results.append(result)
        time.sleep(0.1)
    
    # Test footer pages
    print("\n" + "=" * 70)
    print("TESTING: Footer Pages")
    print("=" * 70)
    
    footer_pages = [
        ('/privacy', 'Privacy Policy'),
        ('/terms', 'Terms of Service'),
        ('/faqs', 'FAQs')
    ]
    
    for url, name in footer_pages:
        result = test_page(url, name)
        page_results.append(result)
        time.sleep(0.1)
    
    # Test special pages
    print("\n" + "=" * 70)
    print("TESTING: Test Pages")
    print("=" * 70)
    
    test_pages = [
        ('/camera-test', 'Camera Test'),
        ('/responsive-test', 'Responsive Test')
    ]
    
    for url, name in test_pages:
        result = test_page(url, name)
        page_results.append(result)
        time.sleep(0.1)
    
    # Test authentication APIs
    print("\n" + "=" * 70)
    print("TESTING: Authentication APIs")
    print("=" * 70)
    
    auth_results = []
    auth_apis = [
        ('/api/auth/status', 'GET', 'Auth Status Check'),
        ('/api/auth/login', 'POST', 'Login Endpoint'),
        ('/api/auth/signup', 'POST', 'Signup Endpoint'),
        ('/api/auth/logout', 'POST', 'Logout Endpoint')
    ]
    
    for url, method, name in auth_apis:
        result = test_api(url, method, name)
        auth_results.append(result)
        time.sleep(0.1)
    
    # Test disease APIs
    print("\n" + "=" * 70)
    print("TESTING: Disease & Prediction APIs")
    print("=" * 70)
    
    disease_results = []
    disease_apis = [
        ('/api/diseases', 'GET', 'Disease List'),
        ('/api/health', 'GET', 'Health Check')
    ]
    
    for url, method, name in disease_apis:
        result = test_api(url, method, name)
        disease_results.append(result)
        time.sleep(0.1)
    
    # Test user APIs (should return 401 if not logged in, which is OK)
    print("\n" + "=" * 70)
    print("TESTING: User-specific APIs (May require authentication)")
    print("=" * 70)
    
    user_results = []
    user_apis = [
        ('/api/notifications', 'GET', 'Notifications'),
        ('/api/history', 'GET', 'Prediction History'),
        ('/api/user/predictions', 'GET', 'User Predictions'),
        ('/api/user/statistics', 'GET', 'User Statistics'),
        ('/api/analytics/summary', 'GET', 'Analytics Summary'),
        ('/api/analytics/daily', 'GET', 'Daily Analytics')
    ]
    
    for url, method, name in user_apis:
        result = test_api(url, method, name)
        user_results.append(result)
        time.sleep(0.1)
    
    # Summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    
    total_pages = len(page_results)
    passed_pages = sum(page_results)
    
    total_auth = len(auth_results)
    passed_auth = sum(auth_results)
    
    total_disease = len(disease_results)
    passed_disease = sum(disease_results)
    
    total_user = len(user_results)
    passed_user = sum(user_results)
    
    print(f"Main Pages: {passed_pages}/{total_pages} passed")
    print(f"Auth APIs: {passed_auth}/{total_auth} passed")
    print(f"Disease APIs: {passed_disease}/{total_disease} passed")
    print(f"User APIs: {passed_user}/{total_user} passed")
    
    total = total_pages + total_auth + total_disease + total_user
    passed = passed_pages + passed_auth + passed_disease + passed_user
    
    print(f"\nOVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("All user-facing pages and APIs are working correctly!")
        return True
    else:
        percentage = (passed / total) * 100
        print(f"\n⚠ {percentage:.1f}% of tests passed")
        print("Some endpoints may need attention.")
        return False

if __name__ == "__main__":
    main()
