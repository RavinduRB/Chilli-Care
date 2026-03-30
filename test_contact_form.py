"""
Test Contact Form Functionality
Run this to verify the contact form is working correctly
"""

import requests
import json

def test_contact_form():
    """Test the contact form submission"""
    
    base_url = "http://127.0.0.1:5000"
    
    # Test data
    test_message = {
        "name": "Test User",
        "email": "test@example.com",
        "subject": "support",
        "message": "This is a test message from the contact form."
    }
    
    print("Testing Contact Form API...")
    print(f"URL: {base_url}/api/contact")
    print(f"Data: {json.dumps(test_message, indent=2)}")
    print("-" * 50)
    
    try:
        # Send POST request
        response = requests.post(
            f"{base_url}/api/contact",
            json=test_message,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ SUCCESS: Contact form is working!")
            return True
        else:
            print(f"\n❌ FAILED: Status code {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server.")
        print("Make sure the Flask app is running on http://127.0.0.1:5000")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def test_validation():
    """Test form validation"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("\n\nTesting Form Validation...")
    print("-" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Missing Email",
            "data": {
                "name": "Test User",
                "subject": "support",
                "message": "Test message"
            },
            "should_fail": True
        },
        {
            "name": "Invalid Email",
            "data": {
                "name": "Test User",
                "email": "invalid-email",
                "subject": "support",
                "message": "Test message"
            },
            "should_fail": True
        },
        {
            "name": "Missing Name",
            "data": {
                "email": "test@example.com",
                "subject": "support",
                "message": "Test message"
            },
            "should_fail": True
        }
    ]
    
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        try:
            response = requests.post(
                f"{base_url}/api/contact",
                json=test['data'],
                headers={"Content-Type": "application/json"}
            )
            
            if test['should_fail'] and response.status_code == 400:
                print(f"✅ PASS: Validation correctly rejected invalid data")
                print(f"   Response: {response.json().get('message', '')}")
            elif not test['should_fail'] and response.status_code == 200:
                print(f"✅ PASS: Valid data accepted")
            else:
                print(f"❌ FAIL: Unexpected result")
                print(f"   Expected failure: {test['should_fail']}")
                print(f"   Status code: {response.status_code}")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    print("=" * 50)
    print("CONTACT FORM TEST SUITE")
    print("=" * 50)
    print("\n⚠️  Make sure your Flask app is running first!")
    print("    Run: python app.py")
    print("=" * 50 + "\n")
    
    input("Press Enter to start testing...")
    
    # Run tests
    test_contact_form()
    test_validation()
    
    print("\n" + "=" * 50)
    print("Testing Complete!")
    print("=" * 50)
