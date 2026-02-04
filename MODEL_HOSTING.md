# Model Hosting Options for Vercel Deployment

## Problem
Your model files are too large for direct Vercel deployment:
- best_chilli_disease_model.h5: 310MB
- chilli_disease_detection_model_final.h5: 104MB

Vercel has a 250MB deployment size limit.

## Solutions

### Option 1: Use Vercel Blob Storage (Recommended)
1. Install Vercel Blob SDK:
   ```bash
   pip install vercel-blob
   ```

2. Upload your model:
   ```bash
   vercel blob upload best_chilli_disease_model.h5
   ```

3. Update app.py to download from Blob storage at runtime

### Option 2: Use External Storage (AWS S3, Google Cloud Storage)
1. Upload model to cloud storage
2. Download at startup with:
   ```python
   import urllib.request
   MODEL_URL = "https://your-storage-url/model.h5"
   urllib.request.urlretrieve(MODEL_URL, "model.h5")
   ```

### Option 3: Use GitHub Releases
1. Create a GitHub release
2. Attach model file as release asset
3. Download from GitHub in app.py

### Option 4: Use Hugging Face Hub (Best for ML)
1. Create account at huggingface.co
2. Upload model to Hub:
   ```bash
   pip install huggingface_hub
   python -c "from huggingface_hub import HfApi; HfApi().upload_file(path='model.h5', repo_id='your-username/chilli-model')"
   ```
3. Download in app with:
   ```python
   from huggingface_hub import hf_hub_download
   model_path = hf_hub_download(repo_id="your-username/chilli-model", filename="model.h5")
   ```

### Option 5: Deploy to Railway Instead (Easiest)
Railway.app is better suited for ML applications:
1. Connect GitHub repo to Railway
2. Deploy with one click
3. No file size limits
4. Free tier available

**Recommended:** Use Railway or Render for ML apps with large models.
