# 📧 Gmail Email Setup Guide

## Current Status
✅ Flask-Mail installed  
✅ Email code added to contact form  
⚠️ **Gmail credentials needed**

## How It Works Now

When someone submits the contact form:
1. ✅ Message is saved to MongoDB database
2. ✅ Email is sent to your Gmail address
3. ✅ User sees success message

---

## 🔑 Step-by-Step: Get Gmail App Password

### Why App Password?
Google doesn't allow apps to use your regular Gmail password for security reasons. You need a special "App Password" instead.

### Steps:

#### 1️⃣ Enable 2-Step Verification (Required)
1. Go to: https://myaccount.google.com/security
2. Find "2-Step Verification" section
3. Click "Get Started" and follow the prompts
4. Verify your phone number
5. Turn it ON

#### 2️⃣ Generate App Password
1. Go to: https://myaccount.google.com/apppasswords
   - **OR** Google "google app passwords" and click the first result
2. You might need to sign in again
3. At the bottom, you'll see "App passwords"
4. Click "Select app" → Choose **"Mail"** (or "Other - Custom name")
5. Click "Select device" → Choose **"Other (Custom name)"**
6. Type a name like: **"Chilli Care Website"**
7. Click **"Generate"**
8. Google will show you a 16-character password like: `abcd efgh ijkl mnop`
9. **⚠️ COPY THIS PASSWORD IMMEDIATELY** (you won't see it again)

#### 3️⃣ Add to Your .env File
1. Open the `.env` file in your project
2. Find these lines:
   ```env
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-16-character-app-password
   ```
3. Replace with your actual values:
   ```env
   MAIL_USERNAME=yourname@gmail.com
   MAIL_PASSWORD=abcdefghijklmnop
   ```
   **Note:** Remove the spaces from the App Password

#### 4️⃣ Restart Your Application
```bash
# Stop the running server (Ctrl+C)
# Then restart it
python app.py
```

---

## 🧪 Testing

### Test the Contact Form:
```bash
python test_contact_form.py
```

**What should happen:**
1. ✅ Script sends a test message
2. ✅ Message is saved to MongoDB
3. ✅ Email is sent to your Gmail
4. ✅ Check your Gmail inbox (takes 5-10 seconds)

### Test from the Website:
1. Open: http://127.0.0.1:5000/contact
2. Fill out the form
3. Submit
4. Check your Gmail inbox

---

## 🔧 Troubleshooting

### Error: "Username and Password not accepted"
**Solution:**
- Make sure you're using an **App Password**, not your regular Gmail password
- Check for typos in your email or password
- Verify 2-Step Verification is enabled

### Error: "SMTPAuthenticationError"
**Solution:**
- Double-check your MAIL_USERNAME is correct
- Make sure MAIL_PASSWORD has NO SPACES
- Try generating a new App Password

### Not Receiving Emails
**Check:**
1. ✅ Gmail Spam/Junk folder
2. ✅ Check `.env` file has correct credentials
3. ✅ Restart the Flask app after editing `.env`
4. ✅ Check terminal for error messages

### Still Not Working?
**Debug Steps:**
1. Check the terminal output when submitting the form
2. Look for log messages: `"Contact form email sent..."`
3. If you see errors, they'll appear in red in the terminal

---

## 📋 What You'll Receive

When someone submits the contact form, you'll get an email like this:

```
From: yourname@gmail.com
Subject: New Contact Form Submission: Technical Support

New message from your Chilli Care contact form:

Name: John Farmer
Email: john@example.com
Subject: Technical Support

Message:
I need help identifying a disease on my chilli plants. 
The leaves are turning yellow...

---
Received at: 2026-03-29 14:30:45
```

---

## 🎯 Quick Start Checklist

- [ ] 2-Step Verification enabled on Gmail
- [ ] App Password generated
- [ ] .env file updated with credentials
- [ ] Flask app restarted
- [ ] Test form submitted
- [ ] Email received in Gmail

---

## 🔒 Security Notes

✅ **Do:**
- Keep your .env file private
- Add `.env` to `.gitignore`
- Use App Passwords (more secure)
- Regenerate App Password if compromised

❌ **Don't:**
- Share your App Password
- Commit .env file to Git
- Use your regular Gmail password
- Share your .env file publicly

---

## 💡 Pro Tips

1. **Check Spam Folder:** First time emails might go to spam
2. **Whitelist Yourself:** Mark the first email as "Not Spam"
3. **Create Email Filter:** Auto-label emails from your contact form
4. **Notification Sound:** Set up Gmail notifications for these emails

---

## 📞 Need Help?

If you're still having issues:
1. Check the terminal output for specific error messages
2. Verify MongoDB is connected (messages should still save)
3. Try with a different Gmail account
4. Make sure your internet connection is working

---

**Your contact form is ready! Just add your Gmail credentials and you're all set! 🎉**
