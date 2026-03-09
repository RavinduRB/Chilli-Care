"""
Quick test script for MongoDB integration
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import MongoDB after loading env
from mongodb_database import get_db

def test_mongodb():
    """Test MongoDB connection and data"""
    
    print("="*60)
    print("TESTING MONGODB INTEGRATION")
    print("="*60)
    
    # Get database instance
    db = get_db()
    
    print(f"\n1. Connection Status: {'✅ Connected' if db.connected else '❌ Not Connected'}")
    
    if not db.connected:
        print("\nError: Could not connect to MongoDB")
        print("Check your MONGODB_URI in .env file")
        return False
    
    # Test database collections
    print(f"\n2. Database Collections:")
    collections = db.db.list_collection_names()
    print(f"   Available collections: {', '.join(collections)}")
    
    # Count documents
    print(f"\n3. Document Counts:")
    diseases_count = db.db.diseases.count_documents({})
    users_count = db.db.users.count_documents({})
    predictions_count = db.db.predictions.count_documents({})
    
    print(f"   Diseases: {diseases_count}")
    print(f"   Users: {users_count}")
    print(f"   Predictions: {predictions_count}")
    
    # Test disease retrieval
    print(f"\n4. Disease Data Test:")
    diseases = db.get_all_diseases()
    for disease in diseases:
        print(f"   ✓ {disease['name']} (Severity: {disease['severity']})")
    
    # Test user operations
    print(f"\n5. User Operations Test:")
    test_email = "test_user@example.com"
    
    # Check if test user exists
    existing = db.get_user_by_email(test_email)
    if existing:
        print(f"   ⚠️  Test user already exists: {test_email}")
    else:
        # Create test user
        import bcrypt
        test_password = bcrypt.hashpw("test123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_id = db.create_user(test_email, test_password, 'farmer')
        
        if user_id:
            print(f"   ✅ Created test user: {test_email}")
            
            # Verify user can be retrieved
            user = db.get_user_by_email(test_email)
            if user:
                print(f"   ✅ User retrieval successful")
                print(f"   User ID: {user['_id']}")
                print(f"   User Type: {user['user_type']}")
                
                # Clean up test user
                db.delete_user(test_email)
                print(f"   ✅ Test user deleted")
            else:
                print(f"   ❌ Failed to retrieve user")
        else:
            print(f"   ❌ Failed to create user")
    
    print(f"\n" + "="*60)
    print("MONGODB INTEGRATION TEST COMPLETE")
    print("="*60)
    
    return True


if __name__ == '__main__':
    try:
        test_mongodb()
    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
