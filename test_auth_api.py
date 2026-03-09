"""
Comprehensive Authentication API Test
Tests all authentication endpoints with the Flask app
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_endpoint(method, endpoint, data=None, cookies=None, description=""):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n{description}")
    print(f"Method: {method} | Endpoint: {endpoint}")
    
    try:
        if method == "POST":
            response = requests.post(url, json=data, cookies=cookies)
        elif method == "GET":
            response = requests.get(url, cookies=cookies)
        elif method == "DELETE":
            response = requests.delete(url, cookies=cookies)
        else:
            print(f"❌ Unsupported method: {method}")
            return None, None
        
        print(f"Status: {response.status_code}")
        
        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        except:
            print(f"Response: {response.text}")
            result = None
        
        # Check for success
        if response.status_code in [200, 201]:
            print("✅ Success")
        else:
            print("⚠️  Failed or Expected Error")
        
        return response, result
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to server!")
        print("Make sure Flask app is running: python app.py")
        return None, None
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None, None

def run_tests():
    """Run all authentication tests"""
    
    print_section("AUTHENTICATION API TEST SUITE")
    print("Starting comprehensive authentication tests...")
    print("Make sure the Flask app is running on http://localhost:5000")
    
    # Test credentials
    test_email = f"test_{int(time.time())}@example.com"
    test_password = "password123"
    admin_email = "admin@chillicare.com"
    admin_password = "admin123"
    
    session_cookie = None
    admin_cookie = None
    
    # Test 1: Health Check
    print_section("TEST 1: Health Check")
    test_endpoint("GET", "/api/health", description="Check if API is running")
    
    # Test 2: Auth Status (Not Logged In)
    print_section("TEST 2: Auth Status (Not Logged In)")
    test_endpoint("GET", "/api/auth/status", description="Check authentication status")
    
    # Test 3: Signup - Invalid Email
    print_section("TEST 3: Signup - Invalid Email")
    test_endpoint("POST", "/api/auth/signup", 
                 data={"email": "invalid-email", "password": test_password},
                 description="Test signup with invalid email format")
    
    # Test 4: Signup - Short Password
    print_section("TEST 4: Signup - Short Password")
    test_endpoint("POST", "/api/auth/signup",
                 data={"email": test_email, "password": "123"},
                 description="Test signup with password less than 6 characters")
    
    # Test 5: Signup - Success
    print_section("TEST 5: Signup - New User")
    response, result = test_endpoint("POST", "/api/auth/signup",
                                    data={"email": test_email, "password": test_password},
                                    description="Create new user account")
    
    if response and response.status_code == 201:
        session_cookie = response.cookies.get_dict()
        print(f"Session cookie received: {bool(session_cookie)}")
    
    # Test 6: Auth Status (Logged In)
    print_section("TEST 6: Auth Status (Logged In)")
    test_endpoint("GET", "/api/auth/status",
                 cookies=session_cookie,
                 description="Check authentication status after signup")
    
    # Test 7: Logout
    print_section("TEST 7: Logout")
    test_endpoint("POST", "/api/auth/logout",
                 cookies=session_cookie,
                 description="Logout from user account")
    session_cookie = None
    
    # Test 8: Signup - Duplicate Email
    print_section("TEST 8: Signup - Duplicate Email")
    test_endpoint("POST", "/api/auth/signup",
                 data={"email": test_email, "password": test_password},
                 description="Try to signup with existing email")
    
    # Test 9: Login - Invalid Credentials
    print_section("TEST 9: Login - Invalid Credentials")
    test_endpoint("POST", "/api/auth/login",
                 data={"email": test_email, "password": "wrongpassword"},
                 description="Login with incorrect password")
    
    # Test 10: Login - Success
    print_section("TEST 10: Login - User Success")
    response, result = test_endpoint("POST", "/api/auth/login",
                                    data={"email": test_email, "password": test_password},
                                    description="Login with correct credentials")
    
    if response and response.status_code == 200:
        session_cookie = response.cookies.get_dict()
        print(f"Session cookie received: {bool(session_cookie)}")
    
    # Test 11: Auth Status (Logged In Again)
    print_section("TEST 11: Auth Status (After Login)")
    test_endpoint("GET", "/api/auth/status",
                 cookies=session_cookie,
                 description="Verify logged in status")
    
    # Test 12: Admin Login
    print_section("TEST 12: Admin Login")
    response, result = test_endpoint("POST", "/api/auth/login",
                                    data={"email": admin_email, "password": admin_password},
                                    description="Login as admin")
    
    if response and response.status_code == 200:
        admin_cookie = response.cookies.get_dict()
        print(f"Admin session cookie received: {bool(admin_cookie)}")
    
    # Test 13: Admin Auth Status
    print_section("TEST 13: Admin Auth Status")
    test_endpoint("GET", "/api/auth/status",
                 cookies=admin_cookie,
                 description="Verify admin logged in status")
    
    # Test 14: Admin Dashboard
    print_section("TEST 14: Admin Dashboard Access")
    test_endpoint("GET", "/api/admin/dashboard",
                 cookies=admin_cookie,
                 description="Access admin dashboard")
    
    # Test 15: Admin Logout
    print_section("TEST 15: Admin Logout")
    test_endpoint("POST", "/api/auth/logout",
                 cookies=admin_cookie,
                 description="Logout admin")
    
    # Test 16: User Predictions (Need Login)
    print_section("TEST 16: User Predictions Access")
    test_endpoint("GET", "/api/user/predictions",
                 cookies=session_cookie,
                 description="Access user's predictions")
    
    # Test 17: User Statistics (Need Login)
    print_section("TEST 17: User Statistics Access")
    test_endpoint("GET", "/api/user/statistics",
                 cookies=session_cookie,
                 description="Access user's statistics")
    
    # Test 18: Delete Account
    print_section("TEST 18: Delete User Account")
    test_endpoint("DELETE", "/api/auth/delete-account",
                 cookies=session_cookie,
                 description="Delete user account")
    
    # Test 19: Login After Deletion
    print_section("TEST 19: Login After Account Deletion")
    test_endpoint("POST", "/api/auth/login",
                 data={"email": test_email, "password": test_password},
                 description="Try to login with deleted account")
    
    # Summary
    print_section("TEST SUITE COMPLETE")
    print("\n✅ All authentication tests completed!")
    print("\nTested Features:")
    print("  - User signup with validation")
    print("  - User login/logout")
    print("  - Admin login")
    print("  - Auth status checking")
    print("  - Session management")
    print("  - Account deletion")
    print("  - Protected endpoints")
    print("\nIf all tests passed, your authentication system is working correctly!")

if __name__ == '__main__':
    print("\n" + "🔐 "*20)
    print("CHILLI CARE - AUTHENTICATION TEST SUITE")
    print("🔐 "*20)
    print("\n⚠️  IMPORTANT: Make sure the Flask app is running!")
    print("Run in another terminal: python app.py")
    input("\nPress Enter to start tests...")
    
    run_tests()
