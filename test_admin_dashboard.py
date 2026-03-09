import requests

# Base URL
BASE_URL = "http://127.0.0.1:5000"

# Create a session to maintain cookies
session = requests.Session()

print("=" * 60)
print("TESTING ADMIN DASHBOARD ACCESS")
print("=" * 60)

# Test 1: Try to access dashboard without login (should redirect)
print("\n1. Accessing /admin/dashboard without login...")
response = session.get(f"{BASE_URL}/admin/dashboard", allow_redirects=False)
print(f"   Status Code: {response.status_code}")
print(f"   Expected: 302 (Redirect)")
if response.status_code == 302:
    print("   ✓ PASS: Correctly redirects to home")
else:
    print("   ✗ FAIL: Should redirect")

# Test 2: Login as admin
print("\n2. Logging in as admin...")
login_data = {
    "email": "admin@chillicare.com",
    "password": "admin123"
}
response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
print(f"   Status Code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        print(f"   ✓ PASS: Login successful")
        print(f"   User Type: {data['user']['user_type']}")
    else:
        print(f"   ✗ FAIL: {data.get('error', 'Unknown error')}")
else:
    print(f"   ✗ FAIL: Status {response.status_code}")
    print(f"   Response: {response.text}")

# Test 3: Try to access dashboard after login (should work)
print("\n3. Accessing /admin/dashboard after login...")
response = session.get(f"{BASE_URL}/admin/dashboard", allow_redirects=False)
print(f"   Status Code: {response.status_code}")
print(f"   Expected: 200 (Success)")
if response.status_code == 200:
    print("   ✓ PASS: Dashboard accessible")
    print(f"   Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
    if 'text/html' in response.headers.get('Content-Type', ''):
        print("   ✓ HTML page returned successfully")
else:
    print(f"   ✗ FAIL: Expected 200, got {response.status_code}")
    print(f"   Response: {response.text[:200]}")

# Test 4: Access dashboard API data
print("\n4. Fetching dashboard data from API...")
response = session.get(f"{BASE_URL}/api/admin/dashboard")
print(f"   Status Code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        print("   ✓ PASS: Dashboard API working")
        print(f"   Total Users: {data['statistics']['total_users']}")
        print(f"   Total Farmers: {data['statistics']['total_farmers']}")
        print(f"   Total Predictions: {data['statistics']['total_predictions']}")
    else:
        print(f"   ✗ FAIL: {data.get('error', 'Unknown error')}")
else:
    print(f"   ✗ FAIL: Status {response.status_code}")

print("\n" + "=" * 60)
print("TESTING COMPLETE")
print("=" * 60)
