#!/usr/bin/env python
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Check environment variables  
print("="*60)
print("ENVIRONMENT CHECK")
print("="*60)
mongodb_uri = os.getenv('MONGODB_URI', '')
print(f"✓ MONGODB_URI exists: {bool(mongodb_uri)}")
if mongodb_uri:
    # Hide password in output
    safe_uri = mongodb_uri.split('@')[1] if '@' in mongodb_uri else mongodb_uri[:50]
    print(f"  URI suffix: ...@{safe_uri}")
print()

# Test import
print("="*60)
print("TESTING MONGODB MODULE")
print("="*60)
try:
    from mongodb_database import get_db
    mongodb = get_db()
    print(f"✓ MongoDB imported")
    print(f"  Connected: {mongodb.connected if mongodb else False}")
    print(f"  Client exists: {mongodb.client is not None if mongodb else False}")
    
    if mongodb and mongodb.connected:
        print(f"  Database: {mongodb.db.name}")
        # Test admin user
        admin = mongodb.get_user_by_email('admin@chillicare.com')
        if admin:
            print(f"✓ Admin user found!")
            print(f"  Email: {admin['email']}")
            print(f"  Type: {admin['user_type']}")
        else:
            print("✗ Admin user not found")
    else:
        print("✗ MongoDB not connected")
        if mongodb and mongodb.client:
            print(f"  Error: Connection timeout or network issue")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
