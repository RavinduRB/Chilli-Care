# Contact Page Setup Guide

## ✅ What's Already Done

Your contact page is now **fully functional** with:

1. **Frontend Form** ([templates/contact.html](templates/contact.html))
   - Professional design with contact information
   - Form fields: Name, Email, Subject, Message
   - Real-time validation
   - Loading states and success/error messages
   - Fully responsive for mobile devices

2. **Backend API** ([app.py](app.py))
   - `/api/contact` endpoint to handle submissions
   - Input validation (required fields, email format)
   - MongoDB integration (stores messages in database)
   - ✅ **Email notifications to Gmail** (NEW!)
   - Error handling

3. **JavaScript Handler**
   - AJAX form submission
   - User-friendly feedback
   - Form auto-reset after success

4. **✅ Email Integration (NEW!)**
   - Flask-Mail installed and configured
   - Automatic email notifications to your Gmail
   - Messages saved to database AND sent via email

## 🚀 How to Use

### 1. Start Your Server
```bash
python app.py
```

### 2. Access the Contact Page
Open your browser and navigate to:
```
http://127.0.0.1:5000/contact
```

### 3. Test the Form
Run the test script:
```bash
python test_contact_form.py
```

## 📋 What Happens When Someone Submits

1. **User fills out the form** on `/contact`
2. **JavaScript validates** the input
3. **Form data is sent** to `/api/contact` endpoint
4. **Backend validates** the data
5. **Message is stored** in MongoDB (`contact_messages` collection)
6. ✅ **Email is sent** to your Gmail address
7. **User sees confirmation** message
8. **Form auto-resets** for another submission

## 📊 Viewing Contact Messages

### Option 1: MongoDB Compass (GUI)
1. Open MongoDB Compass
2. Connect to your database
3. Navigate to: `chilli_care_db` → `contact_messages`
4. View all submissions with timestamps

### Option 2: Python Script
Create a script to view messages:

```python
from mongodb_database import MongoDBManager

db_manager = MongoDBManager()
messages = db_manager.db.contact_messages.find().sort('timestamp', -1)

for msg in messages:
    print(f"\n--- Message from {msg['name']} ({msg['email']}) ---")
    print(f"Subject: {msg['subject']}")
    print(f"Message: {msg['message']}")
    print(f"Received: {msg['timestamp']}")
    print(f"Status: {msg['status']}")
```

### Option 3: Add Admin Dashboard View
You can add a contact messages view to your admin dashboard (recommended).

## 📧 Email Notifications - Setup Required! ⚠️

✅ **Email functionality is already installed and configured!**  
⚠️ **You just need to add your Gmail credentials**

### Quick Setup (3 minutes):

1. **Open [EMAIL_SETUP_GUIDE.md](EMAIL_SETUP_GUIDE.md)** - detailed instructions
2. **Get Gmail App Password** - https://myaccount.google.com/apppasswords
3. **Update .env file** with your credentials:
   ```env
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-16-character-app-password
   ```
4. **Restart your Flask app**

**That's it!** Contact form messages will now be sent to your Gmail inbox.

See [EMAIL_SETUP_GUIDE.md](EMAIL_SETUP_GUIDE.md) for detailed step-by-step instructions.
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'

mail = Mail(app)
```

### Step 3: Update Contact Route
Replace the TODO comment in `/api/contact` with:

```python
# Send email notification
try:
    msg = Message(
        subject=f"New Contact Form: {data['subject']}",
        recipients=['your-email@gmail.com'],
        body=f"""
New contact form submission:

From: {data['name']} ({data['email']})
Subject: {data['subject']}

Message:
{data['message']}

---
Received: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
    )
    mail.send(msg)
except Exception as e:
    logger.error(f"Email sending failed: {str(e)}")
    # Continue anyway - message is still saved in database
```

### Gmail Setup
If using Gmail:
1. Enable 2-Factor Authentication
2. Generate an "App Password" at: https://myaccount.google.com/apppasswords
3. Use the app password in `MAIL_PASSWORD`

## 🔒 Security Considerations

### Rate Limiting (Recommended)
Add rate limiting to prevent spam:

```bash
pip install flask-limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/contact', methods=['POST'])
@limiter.limit("5 per hour")  # Max 5 submissions per hour per IP
def submit_contact():
    # ... existing code ...
```

### CAPTCHA (For High-Traffic Sites)
Consider adding Google reCAPTCHA for additional protection:
- Frontend: Add reCAPTCHA widget
- Backend: Verify token before processing

## 📝 Customization

### Update Contact Information
Edit [templates/contact.html](templates/contact.html) and change:
- Email addresses (lines 55-56)
- Phone numbers (lines 67-68)
- Office address (lines 79-80)
- Working hours (lines 91-93)
- Social media links (bottom of contact info section)

### Change Form Fields
To add/remove fields:
1. Update HTML form in `contact.html`
2. Update validation in `app.py` `/api/contact` route
3. Update JavaScript form handler

### Customize Success/Error Messages
In `app.py`, change the response messages:
```python
return jsonify({
    'success': True,
    'message': 'Your custom success message!'
}), 200
```

## 🐛 Troubleshooting

### Form Not Submitting
1. Check browser console for JavaScript errors (F12)
2. Verify Flask server is running
3. Check network tab to see API response

### Messages Not Saving
1. Verify MongoDB is running: `python test_mongo_connection.py`
2. Check Flask logs for errors
3. Verify `db_manager` is initialized

### 400 Bad Request
- Check all required fields are filled
- Verify email format is valid
- Check browser console for details

### 500 Internal Server Error
- Check Flask terminal for error logs
- Verify MongoDB connection
- Check app.py for syntax errors

## 📱 Mobile Testing

The contact page is fully responsive. Test on:
- Mobile phones (< 768px width)
- Tablets (768px - 1024px)
- Desktop (> 1024px)

## 🎨 Styling

The page uses:
- CSS variables from `base.html`
- Inline styles for component-specific design
- Responsive media queries
- Font Awesome icons

## 📈 Analytics

Consider tracking:
- Form submission rate
- Most common subjects
- Response time to messages
- User satisfaction (follow-up survey)

## 🔗 Integration with Admin Dashboard

To view contact messages in admin dashboard, add to `admin_dashboard.html`:

```python
@app.route('/admin/api/contact-messages')
@login_required
@admin_required
def get_contact_messages():
    """Get all contact messages for admin"""
    try:
        messages = list(db_manager.db.contact_messages
            .find()
            .sort('timestamp', -1)
            .limit(50))
        
        # Convert ObjectId to string
        for msg in messages:
            msg['_id'] = str(msg['_id'])
            msg['timestamp'] = msg['timestamp'].isoformat()
        
        return jsonify({'success': True, 'messages': messages})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

## ✅ Testing Checklist

- [ ] Form loads correctly
- [ ] All fields are required
- [ ] Email validation works
- [ ] Submit button shows loading state
- [ ] Success message appears after submission
- [ ] Form resets after success
- [ ] Error messages display correctly
- [ ] Messages save to MongoDB
- [ ] Mobile responsive design works
- [ ] Social media icons display

## 📞 Support

Your contact page is ready to use! Users can now reach out to you through:
- Contact form (primary method)
- Email addresses shown on page
- Phone numbers shown on page
- Social media links

---

**Next Steps:**
1. Update contact information with your real details
2. Test the form thoroughly
3. Set up email notifications (optional)
4. Add rate limiting for security
5. Create admin view for messages
