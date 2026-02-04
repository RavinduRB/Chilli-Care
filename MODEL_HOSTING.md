# Model Hosting for Vercel Deployment

## Problem
Your model files are too large for Vercel:
- `best_chilli_disease_model.h5`: 310MB
- `chilli_disease_detection_model_final.h5`: 104MB
- Vercel limit: 50MB per deployment

## Solutions

### Option 1: Host on Hugging Face Hub (Recommended - FREE)

1. **Create Hugging Face account:** https://huggingface.co/join

2. **Install Hugging Face CLI:**
   ```bash
   pip install huggingface_hub
   ```

3. **Login:**
   ```bash
   huggingface-cli login
   ```

4. **Upload your model:**
   ```bash
   # Create a new repository
   huggingface-cli repo create chilli-disease-model --type model
   
   # Upload model file
   huggingface-cli upload RavinduRB/chilli-disease-model ./best_chilli_disease_model.h5 best_chilli_disease_model.h5
   huggingface-cli upload RavinduRB/chilli-disease-model ./class_names.json class_names.json
   ```

5. **Model will be accessible at:**
   ```
   https://huggingface.co/RavinduRB/chilli-disease-model/resolve/main/best_chilli_disease_model.h5
   ```

6. **Update app.py to download from Hugging Face:**
   ```python
   import requests
   
   MODEL_URL = "https://huggingface.co/RavinduRB/chilli-disease-model/resolve/main/best_chilli_disease_model.h5"
   CLASS_NAMES_URL = "https://huggingface.co/RavinduRB/chilli-disease-model/resolve/main/class_names.json"
   
   def download_file(url, destination):
       if not os.path.exists(destination):
           logger.info(f"Downloading {destination}...")
           response = requests.get(url, stream=True)
           with open(destination, 'wb') as f:
               for chunk in response.iter_content(chunk_size=8192):
                   f.write(chunk)
           logger.info(f"Download complete: {destination}")
   
   def load_model_and_classes():
       global model, class_names
       
       model_path = "/tmp/best_chilli_disease_model.h5"
       classes_path = "/tmp/class_names.json"
       
       # Download model and classes
       download_file(MODEL_URL, model_path)
       download_file(CLASS_NAMES_URL, classes_path)
       
       # Load model
       model = keras.models.load_model(model_path)
       
       # Load class names
       with open(classes_path, 'r') as f:
           class_names = json.load(f)
   ```

### Option 2: GitHub Releases (FREE)

1. **Create a new release on GitHub:**
   - Go to: https://github.com/RavinduRB/Chilli-Care/releases/new
   - Tag version: v1.0.0
   - Release title: Model Files v1.0.0
   - Upload: `best_chilli_disease_model.h5` and `class_names.json`
   - Publish release

2. **Get download URL:**
   ```
   https://github.com/RavinduRB/Chilli-Care/releases/download/v1.0.0/best_chilli_disease_model.h5
   ```

3. **Use same download code as Hugging Face option**

### Option 3: Google Drive (FREE but may have rate limits)

1. **Upload model to Google Drive**

2. **Get shareable link:** Right-click → Share → Anyone with link

3. **Extract file ID from link:**
   ```
   https://drive.google.com/file/d/FILE_ID_HERE/view?usp=sharing
   ```

4. **Use gdown to download:**
   ```python
   import gdown
   
   def load_model_and_classes():
       model_path = "/tmp/model.h5"
       file_id = "YOUR_FILE_ID"
       
       if not os.path.exists(model_path):
           url = f"https://drive.google.com/uc?id={file_id}"
           gdown.download(url, model_path, quiet=False)
       
       model = keras.models.load_model(model_path)
   ```

### Option 4: Deploy Entire App to Better Platform

Instead of Vercel, use these ML-friendly platforms:

#### Render (Recommended)
```bash
# No size limits, free tier available
# Deploy directly from GitHub
```
1. Go to https://render.com
2. New → Web Service
3. Connect GitHub repo
4. Settings:
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

#### Hugging Face Spaces (Best for ML)
```bash
# Optimized for ML models
# Free GPU available
```
1. Create Space: https://huggingface.co/spaces
2. Choose Gradio or Streamlit
3. Push your code

#### Railway
```bash
# $5/month credit free
# Easy deployment
```
1. Go to https://railway.app
2. New Project → Deploy from GitHub
3. Select repository

## Quick Setup Script

Save this as `setup_model_hosting.py`:

```python
import os
import requests

def upload_to_huggingface():
    """Upload model to Hugging Face Hub"""
    os.system("pip install huggingface_hub")
    os.system("huggingface-cli login")
    os.system("huggingface-cli repo create chilli-disease-model --type model")
    os.system("huggingface-cli upload RavinduRB/chilli-disease-model ./best_chilli_disease_model.h5 best_chilli_disease_model.h5")
    os.system("huggingface-cli upload RavinduRB/chilli-disease-model ./class_names.json class_names.json")
    print("\n✅ Model uploaded to Hugging Face!")
    print("URL: https://huggingface.co/RavinduRB/chilli-disease-model")

if __name__ == "__main__":
    upload_to_huggingface()
```

## Recommended Approach

For your Chilli Care app, I recommend:

1. **For Model Hosting:** Hugging Face Hub (free, reliable, fast CDN)
2. **For App Hosting:** Render or Railway (better for ML apps than Vercel)

This gives you:
- Free hosting
- No size limits
- Better performance for ML inference
- Easier scaling

## Next Steps

1. Choose hosting option
2. Upload model
3. Update `app.py` with download code
4. Test locally
5. Deploy to chosen platform
6. Monitor performance
