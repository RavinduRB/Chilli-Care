"""
Verify MongoDB Data
Check what data has been added to the database
"""
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from mongodb_database import get_db

def verify_mongodb_data():
    """Verify all data in MongoDB"""
    
    print("="*60)
    print("MONGODB DATA VERIFICATION")
    print("="*60)
    
    # Get MongoDB instance
    mongodb = get_db()
    
    if not mongodb or not mongodb.connected:
        print("\n❌ Error: Could not connect to MongoDB!")
        return False
    
    print(f"\n✅ Connected to MongoDB: {mongodb.db.name}\n")
    
    # Check diseases
    print("-"*60)
    print("DISEASES COLLECTION")
    print("-"*60)
    
    diseases = mongodb.get_all_diseases()
    print(f"Total Diseases: {len(diseases)}")
    
    if diseases:
        for disease in diseases:
            print(f"\n  • {disease['name']}")
            print(f"    Severity: {disease.get('severity', 'N/A')}")
            print(f"    Symptoms: {len(disease.get('symptoms', []))} items")
            print(f"    Treatment: {len(disease.get('treatment', []))} items")
            print(f"    Prevention: {len(disease.get('prevention', []))} items")
    
    # Check users
    print("\n" + "-"*60)
    print("USERS COLLECTION")
    print("-"*60)
    
    try:
        users = list(mongodb.db.users.find())
        print(f"Total Users: {len(users)}")
        
        if users:
            admin_count = sum(1 for u in users if u.get('user_type') == 'admin')
            regular_count = len(users) - admin_count
            
            print(f"  Admin Users: {admin_count}")
            print(f"  Regular Users: {regular_count}")
            
            print("\nUser Details:")
            for user in users:
                print(f"\n  • Email: {user['email']}")
                print(f"    Type: {user.get('user_type', 'N/A')}")
                print(f"    Created: {user.get('created_at', 'N/A')}")
    except Exception as e:
        print(f"❌ Error fetching users: {e}")
    
    # Check predictions
    print("\n" + "-"*60)
    print("PREDICTIONS COLLECTION")
    print("-"*60)
    
    try:
        predictions = list(mongodb.db.predictions.find().limit(5))
        total_predictions = mongodb.db.predictions.count_documents({})
        
        print(f"Total Predictions: {total_predictions}")
        
        if predictions:
            print("\nRecent Predictions (last 5):")
            for pred in predictions:
                print(f"\n  • Disease: {pred.get('predicted_disease', 'N/A')}")
                print(f"    Confidence: {pred.get('confidence', 0):.4f}%")
                print(f"    Timestamp: {pred.get('timestamp', 'N/A')}")
    except Exception as e:
        print(f"❌ Error fetching predictions: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("DATABASE SUMMARY")
    print("="*60)
    print(f"✅ Diseases: {len(diseases)} records")
    print(f"✅ Users: {len(users)} records")
    print(f"✅ Predictions: {total_predictions} records")
    print("="*60)
    
    return True


if __name__ == '__main__':
    print("\n📊 CHILLI CARE - DATABASE VERIFICATION 📊\n")
    verify_mongodb_data()
    print("\n")
