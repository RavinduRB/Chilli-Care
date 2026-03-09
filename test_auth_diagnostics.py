"""
Test script to identify authentication issues
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("="*60)
print("AUTHENTICATION SYSTEM DIAGNOSTICS")
print("="*60)

# Test 1: MongoDB Connection
print("\n1. Testing MongoDB Connection...")
try:
    from mongodb_database import get_db
    mongodb = get_db()
    
    if mongodb and mongodb.connected:
        print("   ✅ MongoDB Connected Successfully")
        print(f"   Database: {mongodb.db.name}")
        print(f"   Collections: {mongodb.db.list_collection_names()}")
    else:
        print("   ❌ MongoDB Not Connected")
        print("   Check MONGODB_URI in .env file")
except Exception as e:
    print(f"   ❌ MongoDB Error: {str(e)}")

# Test 2: Environment Variables
print("\n2. Testing Environment Variables...")
mongodb_uri = os.getenv('MONGODB_URI', '')
admin_email = os.getenv('ADMIN_EMAIL', 'admin@chillicare.com')
admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')

print(f"   MONGODB_URI: {'✅ Set' if mongodb_uri else '❌ Missing'}")
print(f"   ADMIN_EMAIL: {admin_email}")
print(f"   ADMIN_PASSWORD: {'✅ Set' if admin_password else '❌ Missing'}")
print(f"   SECRET_KEY: {'✅ Set' if secret_key != 'your-secret-key-here-change-in-production' else '⚠️  Using default'}")

# Test 3: User Operations
print("\n3. Testing User Operations...")
try:
    import bcrypt
    from mongodb_database import get_db
    
    mongodb = get_db()
    
    if mongodb and mongodb.connected:
        # Test create user
        test_email = "diagnostic_test@example.com"
        test_password = "test123"
        
        # Delete if exists
        mongodb.delete_user(test_email)
        
        # Create user
        password_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_id = mongodb.create_user(test_email, password_hash, 'farmer')
        
        if user_id:
            print(f"   ✅ User Creation: Success (ID: {user_id})")
            
            # Test get user by email
            user = mongodb.get_user_by_email(test_email)
            if user:
                print(f"   ✅ Get User by Email: Success")
                
                # Test password verification
                if bcrypt.checkpw(test_password.encode('utf-8'), user['password'].encode('utf-8')):
                    print(f"   ✅ Password Verification: Success")
                else:
                    print(f"   ❌ Password Verification: Failed")
                
                # Test get user by ID
                user_by_id = mongodb.get_user_by_id(str(user['_id']))
                if user_by_id:
                    print(f"   ✅ Get User by ID: Success")
                else:
                    print(f"   ❌ Get User by ID: Failed")
                
                # Test delete user
                if mongodb.delete_user(test_email):
                    print(f"   ✅ Delete User: Success")
                else:
                    print(f"   ❌ Delete User: Failed")
            else:
                print(f"   ❌ Get User by Email: Failed")
        else:
            print(f"   ❌ User Creation: Failed")
    else:
        print("   ❌ Cannot test - MongoDB not connected")
        
except Exception as e:
    print(f"   ❌ User Operations Error: {str(e)}")
    import traceback
    traceback.print_exc()

# Test 4: Flask-Login Integration
print("\n4. Testing Flask-Login Integration...")
try:
    from flask import Flask
    from flask_login import LoginManager, UserMixin
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    # Test User class
    class User(UserMixin):
        def __init__(self, user_id, email, user_type):
            self.id = user_id
            self.email = email
            self.user_type = user_type
        
        def get_id(self):
            return str(self.id)
    
    # Test user creation
    test_user = User('test_id_123', 'test@example.com', 'farmer')
    admin_user = User('admin', 'admin@chillicare.com', 'admin')
    
    print(f"   ✅ User Class: Working")
    print(f"   Test User ID: {test_user.get_id()}")
    print(f"   Admin User ID: {admin_user.get_id()}")
    
except Exception as e:
    print(f"   ❌ Flask-Login Error: {str(e)}")
    import traceback
    traceback.print_exc()

# Test 5: Admin Login
print("\n5. Testing Admin Configuration...")
try:
    from mongodb_database import get_db
    mongodb = get_db()
    
    if mongodb and mongodb.connected:
        # Check if admin exists in database
        admin = mongodb.get_user_by_email("admin@chillicare.com")
        
        if admin:
            print(f"   ✅ Admin found in database: admin@chillicare.com")
            print(f"   ✅ Admin user type: {admin.get('user_type')}")
            print(f"   ✅ Admin stored in MongoDB (not env variables)")
        else:
            print(f"   ⚠️  Admin user not found in database")
            print(f"   Run: python create_admin.py")
    else:
        print("   ❌ Cannot check admin - MongoDB not connected")
except Exception as e:
    print(f"   ❌ Error checking admin: {e}")

print("\n" + "="*60)
print("DIAGNOSTICS COMPLETE")
print("="*60)

# Summary
print("\nSUMMARY:")
print("- If MongoDB connection fails, check MONGODB_URI in .env")
print("- If user operations fail, check MongoDB database permissions")
print("- Admin credentials are now stored in MongoDB database")
print("- Run 'python create_admin.py' to create/update admin user")
print("- Regular users are stored in MongoDB database")
