# Vercel Deployment Guide for Chilli Care

## Prerequisites
- GitHub repository: https://github.com/RavinduRB/Chilli-Care
- Vercel account (sign up at vercel.com)

## Deployment Steps

### 1. Prepare Your Repository
Make sure all configuration files are committed:
```bash
git add vercel.json requirements.txt .vercelignore
git commit -m "Add Vercel configuration"
git push origin main
```

### 2. Deploy to Vercel

#### Option A: Using Vercel Dashboard
1. Go to https://vercel.com
2. Sign in with GitHub
3. Click "Add New" → "Project"
4. Import your repository: `RavinduRB/Chilli-Care`
5. Configure:
   - Framework Preset: Other
   - Root Directory: ./
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
6. Click "Deploy"

#### Option B: Using Vercel CLI
```bash
npm i -g vercel
vercel login
vercel --prod
```

### 3. Important Notes

⚠️ **Model Files**: Your ML model files need to be accessible. Options:
- Keep them in the repository (if under 100MB)
- Use Vercel Blob Storage for large files
- Host model files on external storage (AWS S3, Google Cloud Storage)

⚠️ **Uploads Folder**: Vercel has a read-only filesystem. Modify your app to:
- Use `/tmp` directory for temporary files
- Or use Vercel Blob Storage for user uploads

⚠️ **TensorFlow Size**: TensorFlow is large. If deployment fails:
- Use `tensorflow-cpu` instead of `tensorflow`
- Consider using TensorFlow Lite
- Or deploy on Railway/Render instead (better for ML apps)

### 4. Environment Variables
Add in Vercel Dashboard → Settings → Environment Variables:
- `FLASK_ENV=production`
- Any other secrets your app needs

### 5. Alternative Platforms for ML Apps
If Vercel has size limitations, consider:
- **Railway** (railway.app) - Great for ML apps
- **Render** (render.com) - Free tier with good ML support
- **Hugging Face Spaces** - Optimized for ML models
- **Google Cloud Run** - Scalable container service

## Files Created
- `vercel.json` - Vercel configuration
- `.vercelignore` - Files to exclude from deployment
- `VERCEL_DEPLOY.md` - This guide
