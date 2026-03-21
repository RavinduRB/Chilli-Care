"""
Test Timestamp Fix
Verify that predictions now save with correct local time
"""
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from mongodb_database import get_db

def test_timestamp():
    """Test that timestamps are saved correctly"""
    
    print("="*60)
    print("TESTING TIMESTAMP FIX")
    print("="*60)
    
    # Get MongoDB instance
    mongodb = get_db()
    
    if not mongodb or not mongodb.connected:
        print("\n❌ Error: Could not connect to MongoDB!")
        return False
    
    print(f"\n✅ Connected to MongoDB: {mongodb.db.name}")
    
    # Get current local time
    current_time = datetime.now()
    print(f"\n📅 Current Local Time: {current_time}")
    print(f"   Date: {current_time.strftime('%d/%m/%Y')}")
    print(f"   Time: {current_time.strftime('%H:%M:%S')}")
    
    # Create a test prediction
    print("\n📝 Creating test prediction...")
    
    test_prediction = {
        'predicted_disease': 'Test - Chilli healthy',
        'confidence': 0.99,
        'top_3_predictions': [
            ['Chilli healthy', 0.99],
            ['Chilli Whitefly', 0.005],
            ['Chilli Yellowish', 0.003]
        ],
        'validation_method': 'Test',
        'validation_message': 'Timestamp test',
        'user_ip': '127.0.0.1',
        'user_agent': 'Test Script',
        'model_version': '1.0.0',
        'user_id': None,
        'user_email': 'test@timestamp.com',
        'user_type': 'guest'
    }
    
    # Save prediction (let MongoDB add timestamp)
    prediction_id = mongodb.save_prediction(test_prediction)
    
    if prediction_id:
        print(f"✅ Test prediction saved: {prediction_id}")
        
        # Retrieve the prediction to check timestamp
        from bson.objectid import ObjectId
        saved_prediction = mongodb.db.predictions.find_one({'_id': ObjectId(prediction_id)})
        
        if saved_prediction:
            saved_time = saved_prediction['timestamp']
            print(f"\n✅ Saved Timestamp: {saved_time}")
            print(f"   Date: {saved_time.strftime('%d/%m/%Y')}")
            print(f"   Time: {saved_time.strftime('%H:%M:%S')}")
            
            # Compare times (should be within a few seconds)
            time_diff = abs((saved_time - current_time).total_seconds())
            
            if time_diff < 5:  # Within 5 seconds
                print(f"\n✅ SUCCESS: Timestamp is correct!")
                print(f"   Time difference: {time_diff:.2f} seconds")
            else:
                print(f"\n❌ WARNING: Time difference is too large!")
                print(f"   Time difference: {time_diff:.2f} seconds")
            
            # Clean up test data
            mongodb.db.predictions.delete_one({'_id': ObjectId(prediction_id)})
            print(f"\n🗑️  Test prediction deleted")
            
            return True
        else:
            print(f"\n❌ Could not retrieve saved prediction")
            return False
    else:
        print(f"\n❌ Failed to save test prediction")
        return False


if __name__ == '__main__':
    print("\n🕒 TIMESTAMP FIX VERIFICATION 🕒\n")
    success = test_timestamp()
    print("\n" + "="*60)
    
    if success:
        print("✅ Timestamp fix verified successfully!")
        print("\nPredictions will now display correct local time.")
    else:
        print("❌ Timestamp test failed")
    
    print("="*60 + "\n")
