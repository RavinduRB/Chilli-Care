# 🔔 Notification System - Complete Guide

## Overview

Your Chilli Care application now has a fully functional notification system! Users will receive notifications for:
- **Admin Reply Messages** - When admins respond to contact form submissions
- **System Updates** - Important system announcements and updates

---

## ✅ What Has Been Added

### 1. **Frontend Components**
- ✅ Notification bell icon in navigation bar (before profile icon)
- ✅ Notification badge showing unread count
- ✅ Dropdown panel showing recent notifications
- ✅ Modal for viewing all notifications with filters
- ✅ Mobile-responsive notification button
- ✅ Beautiful animations and styling

### 2. **Backend API Endpoints**
- ✅ `GET /api/notifications` - Fetch user notifications
- ✅ `GET /api/notifications/count` - Get unread notification count
- ✅ `POST /api/notifications/<id>/read` - Mark notification as read
- ✅ `POST /api/notifications/mark-all-read` - Mark all as read
- ✅ `POST /api/admin/notifications/broadcast` - Broadcast to all users (Admin only)

### 3. **Database Schema**
- ✅ New `notifications` collection in MongoDB
- ✅ Indexes for performance optimization
- ✅ Database methods for CRUD operations

### 4. **JavaScript Functionality**
- ✅ Real-time notification updates (checks every 30 seconds)
- ✅ Mark as read on click
- ✅ Filter notifications (All, Unread, Admin Replies, System Updates)
- ✅ Time ago formatting
- ✅ XSS protection

---

## 🚀 User Experience

### For Regular Users (Farmers):

1. **Bell Icon**: Shows in navbar when logged in
2. **Badge**: Red badge shows number of unread notifications
3. **Click Bell**: Opens dropdown with 10 most recent notifications
4. **Click Notification**: Marks it as read
5. **View All**: Click "View All Notifications" to see full list with filters

### For Admins:

Admins can:
- Send notifications to individual users
- Broadcast notifications to all users or filtered groups
- Reply to contact form submissions (automatically creates notification)

---

## 📋 Notification Types

### 1. Admin Reply (`admin_reply`)
- **Icon**: Blue reply icon 💬
- **Purpose**: Responses from admin to user queries
- **Example**: Reply to contact form, support responses

### 2. System Update (`system_update`)
- **Icon**: Orange bell icon 🔔
- **Purpose**: Important system announcements
- **Example**: Maintenance notices, new features, updates

---

## 🧪 Testing the System

### Option 1: Run Test Script

```bash
python test_notifications.py
```

This will:
1. Create sample notifications for a user
2. Allow you to broadcast to all users
3. Test the notification system

### Option 2: Create Notifications Programmatically

```python
from mongodb_database import get_db

db = get_db()

# Send notification to specific user
db.create_notification(
    user_email='farmer@example.com',
    notification_type='admin_reply',
    title='Your Question Response',
    message='Thank you for your question. Here is the answer...',
    metadata={'contact_id': '12345'}
)

# Broadcast to all users
db.broadcast_notification(
    notification_type='system_update',
    title='New Feature Released!',
    message='We have added a new disease to our detection system.',
    user_type_filter='farmer'  # or None for all users
)
```

---

## 👨‍💼 Admin Usage Guide

### How to Send Notifications to Users

#### Method 1: Using the API (from Admin Dashboard)

You can add a notification sending interface to your admin dashboard.

**Example API Call:**

```javascript
// Broadcast to all farmers
fetch('/api/admin/notifications/broadcast', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        type: 'system_update',
        title: 'System Maintenance Notice',
        message: 'We will be performing maintenance on Sunday...',
        user_type_filter: 'farmer'  // 'admin', 'farmer', or null for all
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        alert(`Notification sent to ${data.count} users`);
    }
});
```

#### Method 2: Using Python Script

```python
from mongodb_database import get_db

db = get_db()

# Send to specific user
db.create_notification(
    user_email='user@example.com',
    notification_type='admin_reply',
    title='Re: Your Support Request',
    message='We have addressed your concern...'
)

# Broadcast to everyone
db.broadcast_notification(
    notification_type='system_update',
    title='Important Update',
    message='Our system has been updated with new features.',
    user_type_filter=None  # Send to all users
)
```

---

## 🎨 Customization

### Change Check Interval

In [static/js/notifications.js](static/js/notifications.js#L68):

```javascript
// Default: 30 seconds (30000ms)
notificationCheckInterval = setInterval(async () => {
    await updateNotificationCount();
}, 30000);  // Change this value
```

### Modify Notification Limit

In [static/js/notifications.js](static/js/notifications.js#L85):

```javascript
async function loadNotifications(limit = 10, filter = null) {
    // Change limit value (default: 10)
}
```

---

## 🔧 Automatic Notifications

### Contact Form Replies

When you want to reply to a contact form submission, create a notification:

```python
from mongodb_database import get_db

db = get_db()

# Get contact message
contact_message = db.db.contact_messages.find_one({...})

# Send reply notification
db.create_notification(
    user_email=contact_message['email'],
    notification_type='admin_reply',
    title=f"Re: {contact_message['subject']}",
    message='Thank you for contacting us! Here is our response...',
    metadata={
        'contact_message_id': str(contact_message['_id']),
        'original_subject': contact_message['subject']
    }
)
```

---

## 📊 Database Structure

### Notification Document

```javascript
{
    "_id": ObjectId("..."),
    "user_email": "farmer@example.com",
    "type": "admin_reply",  // or "system_update"
    "title": "Your Support Request",
    "message": "We have reviewed your query...",
    "metadata": {
        // Optional additional data
        "contact_id": "12345",
        "admin_name": "Support Team"
    },
    "read": false,
    "created_at": ISODate("2026-03-29T12:00:00Z"),
    "updated_at": ISODate("2026-03-29T12:00:00Z")
}
```

### Indexes

```javascript
notifications.user_email (ascending)
notifications.created_at (descending)
notifications.read (ascending)
notifications.type (ascending)
```

---

## 🎯 Features

### ✅ Implemented
- [x] Notification bell icon in navbar
- [x] Unread notification badge
- [x] Dropdown notification panel
- [x] Full notification modal with filters
- [x] Mobile responsive design
- [x] Auto-refresh every 30 seconds
- [x] Mark as read functionality
- [x] Mark all as read
- [x] Notification types (admin_reply, system_update)
- [x] Broadcast to all users
- [x] Filter by type
- [x] Beautiful UI with animations
- [x] XSS protection
- [x] Time ago formatting

### 🎨 Design Features
- Glassmorphism notification panel
- Smooth animations
- Pulsing badge effect
- Color-coded notification types
- Responsive for all screen sizes
- Dark mode compatible

---

## 🐛 Troubleshooting

### Notifications Not Appearing?

1. **Check if user is logged in**
   - Notification bell only appears when logged in
   
2. **Check database connection**
   - Ensure MongoDB is connected
   
3. **Check console for errors**
   - Open browser DevTools (F12) → Console tab
   
4. **Verify API endpoints**
   - Test: `http://127.0.0.1:5000/api/notifications/count`

### Badge Not Updating?

1. **Check auto-refresh interval**
   - Default: 30 seconds
   - May need to wait or refresh page
   
2. **Check browser console**
   - Look for JavaScript errors

### Creating Notifications Not Working?

1. **Verify user exists in database**
   ```python
   from mongodb_database import get_db
   db = get_db()
   user = db.db.users.find_one({"email": "user@example.com"})
   print(user)
   ```

2. **Check MongoDB indexes**
   - Restart your app to ensure indexes are created

---

## 📚 API Reference

### Get Notifications
```http
GET /api/notifications?limit=20&skip=0&unread_only=false&type=admin_reply
```

**Response:**
```json
{
    "success": true,
    "notifications": [...],
    "unread_count": 5
}
```

### Get Unread Count
```http
GET /api/notifications/count
```

**Response:**
```json
{
    "success": true,
    "unread_count": 5
}
```

### Mark as Read
```http
POST /api/notifications/<notification_id>/read
```

### Mark All as Read
```http
POST /api/notifications/mark-all-read
```

### Broadcast (Admin Only)
```http
POST /api/admin/notifications/broadcast

{
    "type": "system_update",
    "title": "Title Here",
    "message": "Message here",
    "user_type_filter": "farmer"
}
```

---

## 🎉 Summary

You now have a complete notification system! Users will see:

1. **🔔 Bell icon** - Always visible when logged in
2. **🔴 Badge** - Shows unread count
3. **📱 Mobile support** - Works on all devices
4. **🎨 Beautiful UI** - Professional design
5. **⚡ Real-time** - Updates every 30 seconds

**Your system is ready to use! Enjoy! 🚀**

---

## 💡 Next Steps (Optional Enhancements)

Want to add more features? Consider:

- **Push Notifications** - Using Web Push API
- **Email Notifications** - Send emails for critical updates
- **Notification Preferences** - Let users choose what to receive
- **Notification History** - Archive old notifications
- **Read Receipts** - Track when users read notifications
- **Notification Categories** - More specific types
- **Sound Alerts** - Audio notification for new messages

---

**Need Help?** Check the code comments in:
- `templates/base.html` - HTML structure
- `static/css/style.css` - Styling
- `static/js/notifications.js` - JavaScript logic
- `mongodb_database.py` - Database operations
- `app.py` - API endpoints
