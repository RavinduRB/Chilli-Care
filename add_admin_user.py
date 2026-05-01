"""
Automated Admin User Creation for MongoDB
"""
import os
import bcrypt
from dotenv import load_dotenv

# Load environment variables BEFORE importing mongodb_database
load_dotenv()

from mongodb_database import get_db

def add_admin_user():
    """Add admin user to MongoDB automatically"""
    
    print("="*60)
    print("ADDING ADMIN USER TO MONGODB")
    print("="*60)
    
    # Get MongoDB instance
    mongodb = get_db()
    
    if not mongodb or not mongodb.connected:
        print("\n❌ Error: Could not connect to MongoDB!")
        return False
    
    print(f"\n✅ Connected to MongoDB: {mongodb.db.name}")
    
    # Default admin credentials
    admin_email = "adminchillicare001@gmail.com"
    admin_password = "admin@chilli001"
    
    print(f"\nAdmin Credentials:")
    print(f"  Email: {admin_email}")
    print(f"  Password: {admin_password}")
    
    # Check if admin already exists
    existing_admin = mongodb.get_user_by_email(admin_email)
    
    if existing_admin:
        print(f"\n⚠️  Admin user already exists!")
        if existing_admin.get('user_type') == 'admin':
            print("✅ User is already an admin")
            return True
        else:
            print("📝 Promoting user to admin...")
            password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            result = mongodb.db.users.update_one(
                {'email': admin_email},
                {'$set': {
                    'user_type': 'admin',
                    'password': password_hash
                }}
            )
            
            if result.modified_count > 0:
                print("✅ User promoted to admin successfully!")
                return True
            else:
                print("❌ Failed to promote user")
                return False
    
    # Create new admin user
    print(f"\n📝 Creating new admin user...")
    
    try:
        # Hash password
        password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create admin user
        user_id = mongodb.create_user(admin_email, password_hash, 'admin')
        
        if user_id:
            print(f"\n✅ Admin user created successfully!")
            print(f"   User ID: {user_id}")
            print(f"   Email: {admin_email}")
            print(f"   Type: admin")
            return True
        else:
            print(f"\n❌ Failed to create admin user")
            return False
            
    except Exception as e:
        print(f"\n❌ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("\n🔐 CHILLI CARE - ADDING ADMIN USER 🔐\n")
    
    success = add_admin_user()
    
    if success:
        print("\n" + "="*60)
        print("✅ SUCCESS - Admin user is ready!")
        print("="*60)
        print("\nLogin Credentials:")
        print("  Email: adminchillicare001@gmail.com")
        print("  Password: admin@chilli001")
        print("\n" + "="*60)
    else:
        print("\n❌ Failed to add admin user")
    
    print("\n")
