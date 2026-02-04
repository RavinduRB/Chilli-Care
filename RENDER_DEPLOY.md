# Deploy Chilli Care to Render

## Quick Deploy Steps

### Option 1: Deploy via Render Dashboard (Recommended)

1. **Push your code to GitHub** (already done)

2. **Go to Render Dashboard**
   - Visit: https://render.com
   - Sign up or log in with GitHub

3. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `RavinduRB/Chilli-Care`

4. **Configure the Service**
   - **Name**: `chilli-care`
   - **Region**: Oregon (US West) or closest to your users
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`

5. **Environment Variables**
   - Add: `PYTHON_VERSION` = `3.11.0`
   - Add: `SECRET_KEY` = (generate a random string)

6. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment

### Option 2: Deploy with render.yaml (Infrastructure as Code)

1. The `render.yaml` file is already configured
2. Go to Render Dashboard → "New" → "Blueprint"
3. Connect your repository
4. Render will automatically detect and use the `render.yaml` configuration

## Important Notes

### Model Files
Your model files are large. Render's free tier has limitations:
- **Best model to use**: `best_chilli_disease_model.h5` (smallest)
- Consider hosting large models on external storage (Google Drive, AWS S3) if deployment fails

### Static Files & Images
- Logo and icon images are not in the repo (in .gitignore)
- Upload them manually after deployment via Render's shell or disk
- Or modify .gitignore to include them

### Environment Variables
Set these in Render Dashboard:
- `SECRET_KEY`: Generate a secure random key
- `PYTHON_VERSION`: 3.11.0

### Build Time
- First deployment: 10-15 minutes (installing TensorFlow)
- Subsequent deployments: 5-10 minutes

## Troubleshooting

**Issue**: Out of memory during build
**Solution**: Remove unused model files, keep only one model

**Issue**: Build timeout
**Solution**: Use a paid Render plan or optimize requirements

**Issue**: Images not loading
**Solution**: Add image files back to git or upload via Render disk

## After Deployment

Your app will be available at:
`https://chilli-care.onrender.com`

Note: Free tier services spin down after 15 minutes of inactivity.
First request after spin-down may take 30-60 seconds.

## Monitoring

- Check logs: Render Dashboard → Your Service → Logs
- View metrics: Render Dashboard → Your Service → Metrics
- Shell access: Render Dashboard → Your Service → Shell
