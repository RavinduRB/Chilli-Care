# Vercel Deployment Guide

## Prerequisites
1. Vercel account (https://vercel.com)
2. Vercel CLI installed: `npm install -g vercel`
3. GitHub repository connected to Vercel

## Deployment Steps

### Method 1: Deploy via Vercel Dashboard (Recommended)

1. **Login to Vercel**
   - Go to https://vercel.com
   - Sign in with your GitHub account

2. **Import Your Repository**
   - Click "Add New Project"
   - Select "Import Git Repository"
   - Choose your GitHub repository: `RavinduRB/Chilli-Care`

3. **Configure Project**
   - Framework Preset: Other
   - Root Directory: ./
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
   - Install Command: (leave empty - Vercel will auto-detect)
   
   **Note**: The `runtime.txt` file specifies Python 3.11 for compatibility with TensorFlow

4. **Environment Variables** (Optional)
   - Add any environment variables if needed
   - Example: `FLASK_ENV=production`

5. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete (usually 2-5 minutes)
   - Your app will be available at: `https://your-project-name.vercel.app`

### Method 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy from Project Directory**
   ```bash
   cd "C:\Users\ASUS\Desktop\Chilli Care"
   vercel
   ```

4. **Follow Prompts**
   - Set up and deploy: Yes
   - Which scope: Select your account
   - Link to existing project: No (first time) / Yes (subsequent deploys)
   - Project name: chilli-care (or your preferred name)
   - Directory: ./
   - Override settings: No

5. **Deploy to Production**
   ```bash
   vercel --prod
   ```

## Important Notes

### Model File Size Considerations
Vercel has limitations:
- **Serverless Function Size Limit**: 50MB (Free tier), 250MB (Pro tier)
- **Your model file** (`best_chilli_disease_model.h5`) may exceed this limit

### Solutions for Large Models:

1. **Use External Storage (Recommended)**
   - Upload model to Google Drive, AWS S3, or Hugging Face
   - Download model at runtime or during build
   
2. **Model Optimization**
   - Quantize the model to reduce size
   - Use TensorFlow Lite format (.tflite)
   - Remove unused layers or compress weights

3. **Alternative: Use Vercel Edge Functions**
   - Deploy lightweight API on Vercel
   - Host model inference on separate service (AWS Lambda, Google Cloud Functions)

### Recommended Deployment Strategy

For models > 50MB, use this approach:

1. **Host model externally**
   ```python
   # In app.py, add model download function
   import urllib.request
   
   def download_model():
       model_url = "https://your-storage/best_chilli_disease_model.h5"
       local_path = "/tmp/model.h5"
       if not os.path.exists(local_path):
           urllib.request.urlretrieve(model_url, local_path)
       return local_path
   ```

2. **Load model on first request**
   ```python
   @app.before_first_request
   def load_model_lazy():
       global model
       model_path = download_model()
       model = keras.models.load_model(model_path)
   ```

## Troubleshooting

### Common Issues:

1. **Build Fails - Module Not Found**
   - Check `requirements_vercel.txt` has all dependencies
   - Use `tensorflow-cpu` instead of `tensorflow` for faster builds

2. **Function Size Exceeded**
   - Reduce model file size
   - Use external model hosting
   - Consider using Vercel Pro plan

3. **Static Files Not Loading**
   - Ensure `vercel.json` routes are configured correctly
   - Check file paths use forward slashes (/)

4. **API Timeout**
   - Vercel serverless functions timeout after 10s (Hobby) / 60s (Pro)
   - Optimize model inference speed
   - Use lazy loading for model

## Testing Deployment

1. **Test Locally First**
   ```bash
   vercel dev
   ```

2. **Check Deployment Status**
   - Visit Vercel Dashboard
   - View deployment logs
   - Check function execution logs

3. **Test API Endpoints**
   ```bash
   curl https://your-app.vercel.app/api/health
   ```

## Additional Resources

- Vercel Documentation: https://vercel.com/docs
- Python on Vercel: https://vercel.com/docs/functions/runtimes/python
- Vercel CLI Reference: https://vercel.com/docs/cli

## Support

For issues specific to this application, please open an issue on the GitHub repository.
