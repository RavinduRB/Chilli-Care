# 🔐 Setting Up Gemini API for Image Validation

## Quick Setup Guide

### Step 1: Get Your Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Get API Key"** or **"Create API Key"**
4. Copy your API key

### Step 2: Configure the Application

**Option A: Using .env file (Recommended)**

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and add your key:
   ```
   GEMINI_API_KEY=AIzaSyC_your_actual_api_key_here
   ```

**Option B: Using Environment Variable**

Windows (Command Prompt):
```cmd
set GEMINI_API_KEY=your_api_key_here
python app.py
```

Windows (PowerShell):
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
python app.py
```

Linux/Mac:
```bash
export GEMINI_API_KEY=your_api_key_here
python app.py
```

### Step 3: Test the Connection

Run the test script:
```bash
python test_gemini_validation.py
```

You should see:
- ✓ Connection successful!
- API Key Set: Yes ✓

### Step 4: Start the Application

```bash
python app.py
```

## 🧪 Testing Image Validation

### Valid Images (Should Pass):
- ✅ Chilli plant leaves (healthy)
- ✅ Chilli plant leaves (diseased - spots, yellowing, curling)
- ✅ Chilli peppers/fruits
- ✅ Full chilli plants
- ✅ Close-up of chilli plant parts

### Invalid Images (Should Fail):
- ❌ Tomato plants
- ❌ Other vegetables
- ❌ Flowers
- ❌ Animals
- ❌ People
- ❌ Objects
- ❌ Landscapes

## 🔒 Security Best Practices

1. **Never commit `.env` to version control**
   - The `.gitignore` file already includes `.env`
   
2. **Keep your API key secret**
   - Don't share it in screenshots
   - Don't paste it in public forums
   
3. **Monitor your API usage**
   - Check [Google AI Studio](https://makersuite.google.com/) for usage
   - Set up usage alerts if available

4. **Rotate keys regularly**
   - Generate new keys periodically
   - Revoke old keys after rotation

## 📊 API Limits

**Free Tier (Gemini 2.5 Flash):**
- 15 requests per minute (RPM)
- 1 million tokens per minute (TPM)
- 1,500 requests per day (RPD)

For higher limits, check Google's pricing page.

## 🔄 Important Update

**The package has been updated from the deprecated `google-generativeai` to the new `google-genai` package.**

Model names now require the `models/` prefix:
- ✅ Correct: `models/gemini-2.5-flash`
- ❌ Old: `gemini-1.5-flash`

## 🐛 Troubleshooting

### Error: "GEMINI_API_KEY not found"
- Make sure `.env` file exists in the project root
- Check that the key name is exactly `GEMINI_API_KEY`
- Restart your terminal/IDE after creating `.env`

### Error: "API key not valid"
- Verify your key is correct (copy-paste carefully)
- Check if the key is active in Google AI Studio
- Try generating a new key

### Error: "Resource has been exhausted"
- You've hit the rate limit
- Wait a few minutes and try again
- Consider upgrading your quota

### Validation Disabled Warning
If you see "Image validation will be disabled" in logs:
- This means the app works but won't validate images
- Add your API key to enable validation
- All images will be processed without checking

## 🆘 Support

If validation doesn't work but the API key is set:
1. Run `python test_gemini_validation.py`
2. Check the logs for detailed error messages
3. Verify your internet connection
4. Make sure google-genai package is installed:
   ```bash
   pip install google-genai
   ```
5. Run `python list_gemini_models.py` to see available models

## 💡 Pro Tips

1. **During Development**: You can skip setting up Gemini temporarily. The app will log a warning but continue to work.

2. **For Production**: Always set up the API key to prevent false diagnoses.

3. **Testing**: Use the test script to verify everything before deploying.

4. **Batch Processing**: If processing many images, be mindful of rate limits.
