# Deploy Chilli Care to Vercel

## Prerequisites
- Vercel account (free tier available)
- Vercel CLI installed: `npm install -g vercel`

## Important Notes
⚠️ **Vercel has limitations for TensorFlow models:**
- Maximum deployment size: 50MB (your model may exceed this)
- Serverless functions have memory and execution time limits
- Consider using Vercel with model hosted separately (see alternatives below)

## Deployment Steps

### Option 1: Direct Vercel Deployment (If model < 50MB)

1. **Login to Vercel:**
   ```bash
   vercel login
   ```

2. **Deploy from project directory:**
   ```bash
   cd "C:\Users\ASUS\Desktop\Chilli Care"
   vercel
   ```

3. **Follow prompts:**
   - Set up and deploy: Yes
   - Which scope: Your account
   - Link to existing project: No
   - Project name: chilli-care (or your choice)
   - Directory: ./
   - Override settings: No

4. **For production deployment:**
   ```bash
   vercel --prod
   ```

### Option 2: Deploy via GitHub (Recommended)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add Vercel deployment configuration"
   git push origin main
   ```

2. **Import to Vercel:**
   - Go to https://vercel.com/new
   - Import your GitHub repository
   - Configure project:
     - Framework Preset: Other
     - Build Command: (leave empty)
     - Output Directory: (leave empty)
   - Click "Deploy"

### Option 3: Host Model Separately (Best for Large Models)

If your model is too large (>50MB), consider:

1. **Upload model to cloud storage:**
   - Google Cloud Storage
   - AWS S3
   - Hugging Face Hub
   - GitHub Releases

2. **Modify app.py to download model:**
   ```python
   import requests
   
   def load_model_and_classes():
       model_url = "YOUR_MODEL_URL"
       model_path = "/tmp/model.h5"
       
       if not os.path.exists(model_path):
           response = requests.get(model_url)
           with open(model_path, 'wb') as f:
               f.write(response.content)
       
       model = keras.models.load_model(model_path)
       # ... rest of code
   ```

## Check Model Size

Run this in your project directory:
```bash
# Check model file sizes
ls -lh *.h5 *.keras 2>/dev/null

# Total size of critical files
du -sh best_chilli_disease_model.h5
```

## Configuration Files Created

- ✅ `vercel.json` - Vercel configuration
- ✅ `requirements_vercel.txt` - Lightweight dependencies (tensorflow-cpu)
- ✅ `.vercelignore` - Files to exclude from deployment

## Environment Variables (Optional)

If needed, set in Vercel dashboard or CLI:
```bash
vercel env add FLASK_ENV production
vercel env add SECRET_KEY your-secret-key-here
```

## Troubleshooting

### Deployment Size Error
If deployment exceeds 50MB:
- Use Option 3 (host model separately)
- Or deploy to Render/Railway/Heroku instead

### Module Import Errors
- Ensure `requirements_vercel.txt` has all dependencies
- Use `tensorflow-cpu` instead of `tensorflow`

### Serverless Timeout
- Vercel free tier: 10s execution limit
- Upgrade to Pro for 60s limit
- Or use alternative hosting

## Alternative Hosting Options

If Vercel doesn't work well:

1. **Render** (Recommended for ML apps)
   - Free tier available
   - Better for larger apps
   - No size limits

2. **Railway**
   - $5/month credit free
   - Easy deployment

3. **Hugging Face Spaces**
   - Free for ML models
   - Optimized for AI apps

4. **Google Cloud Run**
   - Pay per use
   - Good for containerized apps

## Testing Deployment

After deployment:
```bash
# Test the API
curl https://your-app.vercel.app/api/health

# Upload and test prediction
curl -X POST -F "file=@test_image.jpg" https://your-app.vercel.app/predict
```

## Post-Deployment

1. Add custom domain (optional)
2. Monitor analytics in Vercel dashboard
3. Set up environment variables for production
4. Enable CORS if needed for frontend

## Need Help?

- Vercel Docs: https://vercel.com/docs
- Contact support or check logs in Vercel dashboard
