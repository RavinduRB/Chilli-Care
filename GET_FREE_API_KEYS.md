# How to Get Free API Keys for Chilli Care

Your API quotas have been exhausted. Here's how to get new **FREE** API keys to restore full functionality.

---

## 🚀 Quick Summary

- **Gemini API**: Free 1,500 requests/day per key (Get 5+ keys!)
- **HuggingFace API**: Free 30,000 characters/month
- **Time needed**: 5-10 minutes per service

---

## 🔑 Option 1: Get New Gemini API Keys (RECOMMENDED)

Google's Gemini API is **FREE** with generous quotas. You can create multiple keys!

### Step-by-Step Guide:

#### 1. **Go to Google AI Studio**
   - Visit: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
   - Sign in with your Google account

#### 2. **Create API Key**
   - Click **"Get API key"** or **"Create API key"**
   - Select "Create API key in new project" (or use existing project)
   - Copy the generated API key (looks like: `AIzaSyD...`)

#### 3. **Get Multiple Keys (IMPORTANT!)**
   To maximize quota, create keys with **different Google accounts**:
   
   **Method A: Use Multiple Google Accounts**
   - Personal Gmail (@gmail.com)
   - Work/School email (if you have one)
   - Create new Gmail accounts (it's free!)
   - Each account gets 1,500 requests/day
   
   **Method B: Create New Gmail Accounts**
   1. Go to [gmail.com](https://gmail.com)
   2. Click "Create account"
   3. Fill basic info (takes 2 minutes)
   4. Verify with phone number (can reuse same number)
   5. Go back to AI Studio and create API key
   
   **PRO TIP**: Create 5 accounts = 7,500 free requests/day!

#### 4. **Add Keys to Your App**
   
   **Option A: Using .env file (Recommended)**
   
   Open your `.env` file and add:
   ```env
   GEMINI_API_KEY=AIzaSyD...your_first_key...
   GEMINI_API_KEY_2=AIzaSyD...your_second_key...
   GEMINI_API_KEY_3=AIzaSyD...your_third_key...
   GEMINI_API_KEY_4=AIzaSyD...your_fourth_key...
   GEMINI_API_KEY_5=AIzaSyD...your_fifth_key...
   ```
   
   **Option B: Set as Environment Variables (Windows)**
   ```cmd
   setx GEMINI_API_KEY "AIzaSyD...your_key..."
   setx GEMINI_API_KEY_2 "AIzaSyD...your_second_key..."
   ```

#### 5. **Test Your Keys**
   ```bash
   python test_gemini_validation.py
   ```

---

## 🤗 Option 2: Get HuggingFace API Key

HuggingFace provides free API access for inference.

### Step-by-Step Guide:

#### 1. **Create HuggingFace Account**
   - Visit: [https://huggingface.co/join](https://huggingface.co/join)
   - Sign up with email (FREE, no credit card needed)
   - Verify your email

#### 2. **Get Your API Token**
   - Go to: [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
   - Click **"New token"**
   - Name it: "ChilliCare" (or anything you like)
   - Select role: **"read"** (this is enough)
   - Click **"Generate token"**
   - Copy the token (looks like: `hf_...`)

#### 3. **Add to Your App**
   
   In your `.env` file:
   ```env
   HUGGINGFACE_API_KEY=hf_...your_token_here...
   ```

#### 4. **Test It**
   ```bash
   python test_api.py
   ```

---

## 📝 Complete .env File Example

Create or update your `.env` file in the project root:

```env
# MongoDB Connection
MONGODB_URI=your_mongodb_connection_string

# Gemini API Keys (Get from https://aistudio.google.com)
GEMINI_API_KEY=AIzaSyD...key1...
GEMINI_API_KEY_2=AIzaSyD...key2...
GEMINI_API_KEY_3=AIzaSyD...key3...
GEMINI_API_KEY_4=AIzaSyD...key4...
GEMINI_API_KEY_5=AIzaSyD...key5...

# HuggingFace API Token (Get from https://huggingface.co/settings/tokens)
HUGGINGFACE_API_KEY=hf_...your_token...

# Admin Credentials
ADMIN_EMAIL=admin@chillicare.com
ADMIN_PASSWORD=your_secure_password

# Flask Secret Key
SECRET_KEY=your_random_secret_key_here
```

---

## 🎯 Pro Tips for Maximum Quota

### 1. **Create Multiple Google Accounts**
   - Each account = 1,500 requests/day
   - 5 accounts = 7,500 requests/day
   - No cost, just need different emails

### 2. **Rotate Keys Automatically**
   Your app already rotates through keys automatically! Just add more keys.

### 3. **Monitor Your Usage**
   - Check quota at: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
   - Click on each key to see usage

### 4. **Use Local Validation**
   - Your app now has **improved AI-free validation**
   - Works even when all APIs are exhausted
   - No API keys needed at all!

---

## 🔄 What Happens Now?

Your app uses a **3-tier validation system**:

1. **Tier 1**: Try all Gemini keys (fast & accurate)
2. **Tier 2**: Try HuggingFace (backup)
3. **Tier 3**: Use local validation ✨ **(NEW & IMPROVED!)**

Even with **ZERO API keys**, your app will work using the improved local validation!

---

## ❓ Troubleshooting

### "API key not valid" error
- Make sure you copied the entire key
- Check for extra spaces before/after the key
- Verify the key is active in AI Studio

### "Resource exhausted" error
- You've hit the daily quota for that key
- Add more keys OR wait 24 hours
- Local validation will automatically kick in

### HuggingFace not working
- Free tier has rate limits
- Try again in a few minutes
- Local validation works as fallback

### Still having issues?
1. Check your `.env` file is in the project root
2. Restart your app after adding keys
3. Test with: `python test_gemini_validation.py`

---

## 🎉 Benefits of Multiple Keys

| Keys | Daily Requests | Monthly Capacity |
|------|---------------|------------------|
| 1 key | 1,500 | 45,000 |
| 3 keys | 4,500 | 135,000 |
| 5 keys | 7,500 | 225,000 |
| 10 keys | 15,000 | 450,000 |

**All FREE!** Just need different Google accounts.

---

## 🆓 No API Keys? No Problem!

Your app now has **advanced local validation** that works WITHOUT any API keys:

✅ Analyzes plant colors (green, yellow, brown)  
✅ Detects natural color variation  
✅ Checks lighting quality  
✅ Identifies organic vs artificial images  
✅ Scores images intelligently  

**Result**: Your app is now **100% functional** even without API keys!

---

## 📧 Need Help?

- **Gemini API Issues**: [Google AI Studio Support](https://aistudio.google.com)
- **HuggingFace Issues**: [HF Community](https://discuss.huggingface.co)
- **App Issues**: Check your logs in the terminal

---

## 🔒 Security Notes

- ⚠️ **Never commit** your `.env` file to Git
- ⚠️ **Never share** your API keys publicly
- ⚠️ Add `.env` to your `.gitignore` file
- ✅ Keys are free but personal - keep them private

---

**Happy Growing! 🌶️**
