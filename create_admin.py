"""
Create Admin User in MongoDB
This script creates or updates the admin user account in the database
"""
import os
import sys
import bcrypt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_admin():
    """Create admin user in MongoDB"""
    
    print("="*60)
    print("CREATE ADMIN USER IN DATABASE")
    print("="*60)
    
    # Import MongoDB after loading env
    try:
        from mongodb_database import get_db
    except ImportError as e:
        print(f"\n❌ Error: Could not import mongodb_database: {e}")
        return False
    
    # Get MongoDB instance
    mongodb = get_db()
    
    if not mongodb or not mongodb.connected:
        print("\n❌ Error: Could not connect to MongoDB!")
        print("Please check your MONGODB_URI in .env file")
        return False
    
    print(f"\n✅ Connected to MongoDB: {mongodb.db.name}")
    
    # Get admin credentials
    print("\n" + "-"*60)
    print("Enter Admin Credentials")
    print("-"*60)
    
    # Option to use default or custom credentials
    use_default = input("\nUse default admin credentials? (yes/no) [yes]: ").strip().lower()
    
    if use_default == '' or use_default == 'yes' or use_default == 'y':
        admin_email = "admin@chillicare.com"
        admin_password = "admin123"
        print(f"\nUsing default credentials:")
        print(f"  Email: {admin_email}")
        print(f"  Password: {admin_password}")
    else:
        admin_email = input("Admin email: ").strip().lower()
        admin_password = input("Admin password (min 6 characters): ").strip()
        
        # Validate
        if not admin_email or '@' not in admin_email:
            print("❌ Error: Invalid email format")
            return False
        
        if len(admin_password) < 6:
            print("❌ Error: Password must be at least 6 characters")
            return False
    
    # Check if admin already exists
    existing_admin = mongodb.get_user_by_email(admin_email)
    
    if existing_admin:
        print(f"\n⚠️  Admin user already exists: {admin_email}")
        
        # Check if it's already an admin
        if existing_admin.get('user_type') == 'admin':
            print("   User type: admin ✓")
            
            update = input("\nUpdate admin password? (yes/no) [no]: ").strip().lower()
            
            if update == 'yes' or update == 'y':
                # Hash new password
                password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                # Update password
                try:
                    result = mongodb.db.users.update_one(
                        {'email': admin_email},
                        {'$set': {'password': password_hash}}
                    )
                    
                    if result.modified_count > 0:
                        print("\n✅ Admin password updated successfully!")
                        return True
                    else:
                        print("\n⚠️  Password not changed (same as before)")
                        return True
                except Exception as e:
                    print(f"\n❌ Error updating password: {e}")
                    return False
            else:
                print("\n✅ Admin user already configured (no changes made)")
                return True
        else:
            # User exists but not admin - promote to admin
            print(f"   User type: {existing_admin.get('user_type')} - needs promotion")
            
            promote = input("\nPromote this user to admin? (yes/no) [yes]: ").strip().lower()
            
            if promote == '' or promote == 'yes' or promote == 'y':
                # Hash new password
                password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                try:
                    result = mongodb.db.users.update_one(
                        {'email': admin_email},
                        {'$set': {
                            'user_type': 'admin',
                            'password': password_hash
                        }}
                    )
                    
                    if result.modified_count > 0:
                        print("\n✅ User promoted to admin successfully!")
                        return True
                    else:
                        print("\n❌ Failed to promote user")
                        return False
                except Exception as e:
                    print(f"\n❌ Error promoting user: {e}")
                    return False
            else:
                print("\n❌ Aborted - user not promoted")
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
            
            # Verify admin user was created
            admin = mongodb.get_user_by_email(admin_email)
            if admin and admin.get('user_type') == 'admin':
                print("\n✅ Verification: Admin user confirmed in database")
                return True
            else:
                print("\n⚠️  Warning: Could not verify admin user creation")
                return False
        else:
            print(f"\n❌ Failed to create admin user")
            return False
            
    except Exception as e:
        print(f"\n❌ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_admin_info():
    """Show current admin users in database"""
    print("\n" + "="*60)
    print("CURRENT ADMIN USERS IN DATABASE")
    print("="*60)
    
    try:
        from mongodb_database import get_db
        mongodb = get_db()
        
        if not mongodb or not mongodb.connected:
            print("\n❌ Could not connect to MongoDB")
            return
        
        # Get all admin users
        try:
            admins = list(mongodb.db.users.find({'user_type': 'admin'}))
            
            if admins:
                print(f"\nFound {len(admins)} admin user(s):")
                for admin in admins:
                    print(f"\n  • Email: {admin['email']}")
                    print(f"    ID: {admin['_id']}")
                    print(f"    Created: {admin.get('created_at', 'N/A')}")
                    print(f"    Last Login: {admin.get('last_login', 'Never')}")
            else:
                print("\n⚠️  No admin users found in database")
                print("Run this script to create an admin user")
        except Exception as e:
            print(f"\n❌ Error fetching admin users: {e}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == '__main__':
    print("\n🔐 "*20)
    print("CHILLI CARE - ADMIN USER MANAGEMENT")
    print("🔐 "*20)
    
    # Show current admins
    show_admin_info()
    
    # Menu
    print("\n" + "-"*60)
    print("Options:")
    print("  1. Create/Update admin user")
    print("  2. Show admin users")
    print("  3. Exit")
    print("-"*60)
    
    choice = input("\nEnter your choice [1]: ").strip()
    
    if choice == '' or choice == '1':
        success = create_admin()
        if success:
            print("\n" + "="*60)
            print("✅ SUCCESS - Admin user is ready!")
            print("="*60)
            print("\nYou can now login with admin credentials:")
            print("  POST /api/auth/login")
            print("  Body: {\"email\": \"admin@chillicare.com\", \"password\": \"admin123\"}")
            print("\nAdmin users are now stored in MongoDB database.")
    elif choice == '2':
        show_admin_info()
    else:
        print("\n👋 Exiting...")
    
    print("\n")
