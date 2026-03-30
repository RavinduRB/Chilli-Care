"""
Test Notification System
Creates sample notifications to test the notification bell feature
"""

from mongodb_database import get_db
from datetime import datetime

def create_test_notifications():
    """Create test notifications for demonstration"""
    
    db = get_db()
    
    if not db or not db.connected:
        print("❌ Error: MongoDB not connected")
        return
    
    # Get a user email from the database
    user = db.db.users.find_one({"user_type": "farmer"})
    
    if not user:
        print("❌ No farmer users found in database")
        print("Please create a user account first")
        return
    
    user_email = user['email']
    print(f"Creating test notifications for: {user_email}")
    print("-" * 60)
    
    # Sample admin reply notification
    notification_id = db.create_notification(
        user_email=user_email,
        notification_type='admin_reply',
        title='Re: Technical Support Request',
        message='Thank you for contacting us! We have reviewed your query about yellowing leaves. This could be a sign of nutrient deficiency. Please check our treatment guide for more details.',
        metadata={
            'contact_form_id': 'test_12345',
            'admin_name': 'Support Team'
        }
    )
    
    if notification_id:
        print(f"✓ Created admin reply notification (ID: {notification_id})")
    
    # Sample system update notification
    notification_id = db.create_notification(
        user_email=user_email,
        notification_type='system_update',
        title='New Disease Detection Model',
        message='We have updated our AI model with improved accuracy! The new model can now detect 2 additional chilli diseases with 95% accuracy.',
        metadata={
            'version': '2.0',
            'update_date': datetime.now().isoformat()
        }
    )
    
    if notification_id:
        print(f"✓ Created system update notification (ID: {notification_id})")
    
    # Another sample
    notification_id = db.create_notification(
        user_email=user_email,
        notification_type='admin_reply',
        title='Treatment Recommendation Update',
        message='Based on your recent disease detection, we recommend checking the moisture levels in your field. Excess moisture can lead to fungal infections.',
        metadata={
            'prediction_id': 'test_67890'
        }
    )
    
    if notification_id:
        print(f"✓ Created treatment recommendation notification (ID: {notification_id})")
    
    print("-" * 60)
    
    # Check unread count
    unread_count = db.count_unread_notifications(user_email)
    print(f"\n📊 Total unread notifications for {user_email}: {unread_count}")
    print(f"\n✅ Test notifications created successfully!")
    print(f"\n💡 Now refresh your browser and click the bell icon to see them!")


def broadcast_test_notification():
    """Broadcast a test notification to all users"""
    
    db = get_db()
    
    if not db or not db.connected:
        print("❌ Error: MongoDB not connected")
        return
    
    print("Broadcasting test notification to all users...")
    print("-" * 60)
    
    count = db.broadcast_notification(
        notification_type='system_update',
        title='📢 System Maintenance Notice',
        message='We will be performing scheduled maintenance on Sunday, March 31st from 2:00 AM to 4:00 AM. The system may be temporarily unavailable during this time.',
        metadata={
            'scheduled_time': 'March 31, 2026 - 2:00 AM to 4:00 AM',
            'priority': 'medium'
        },
        user_type_filter='farmer'  # Only send to farmers
    )
    
    print(f"✓ Broadcast notification sent to {count} users")
    print(f"✅ Broadcast complete!")


if __name__ == "__main__":
    print("=" * 60)
    print("   NOTIFICATION SYSTEM TEST")
    print("=" * 60)
    print()
    
    print("Choose an option:")
    print("1. Create test notifications for a specific user")
    print("2. Broadcast notification to all farmers")
    print("3. Both")
    print()
    
    choice = input("Enter your choice (1/2/3): ").strip()
    
    print()
    
    if choice == "1":
        create_test_notifications()
    elif choice == "2":
        broadcast_test_notification()
    elif choice == "3":
        create_test_notifications()
        print()
        broadcast_test_notification()
    else:
        print("❌ Invalid choice")
