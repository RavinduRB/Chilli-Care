# Model Hosting Options for Vercel Deployment

## Problem
Your model files (104MB - 310MB) exceed Vercel's serverless function size limit:
- **Free/Hobby Plan**: 50MB limit
- **Pro Plan**: 250MB limit

## Solutions

### Option 1: Hugging Face Hub (Recommended - Free)

1. **Upload Model to Hugging Face**
   ```bash
   pip install huggingface_hub
   huggingface-cli login
   ```

2. **Create Repository and Upload**
   ```python
   from huggingface_hub import HfApi, create_repo
   
   api = HfApi()
   repo_id = "your-username/chilli-disease-model"
   create_repo(repo_id, repo_type="model")
   api.upload_file(
       path_or_fileobj="best_chilli_disease_model.h5",
       path_in_repo="model.h5",
       repo_id=repo_id
   )
   ```

3. **Download in App** (modify app.py)
   ```python
   from huggingface_hub import hf_hub_download
   
   def load_model_from_hf():
       model_path = hf_hub_download(
           repo_id="your-username/chilli-disease-model",
           filename="model.h5",
           cache_dir="/tmp"
       )
       return keras.models.load_model(model_path)
   ```

### Option 2: Google Drive (Public Link)

1. **Upload to Google Drive**
2. **Make File Public and Get Share Link**
3. **Convert to Direct Download Link**
   - Original: `https://drive.google.com/file/d/FILE_ID/view?usp=sharing`
   - Direct: `https://drive.google.com/uc?export=download&id=FILE_ID`

4. **Download in App**
   ```python
   import gdown
   
   def download_model():
       url = "https://drive.google.com/uc?export=download&id=YOUR_FILE_ID"
       output = "/tmp/model.h5"
       gdown.download(url, output, quiet=False)
       return output
   ```

### Option 3: GitHub Releases (For files < 2GB)

1. **Create GitHub Release**
   ```bash
   gh release create v1.0 best_chilli_disease_model.h5
   ```

2. **Download in App**
   ```python
   import urllib.request
   
   def download_model():
       url = "https://github.com/RavinduRB/Chilli-Care/releases/download/v1.0/best_chilli_disease_model.h5"
       output = "/tmp/model.h5"
       urllib.request.urlretrieve(url, output)
       return output
   ```

### Option 4: AWS S3 / CloudFront (Paid)

1. **Upload to S3 Bucket**
2. **Make Publicly Accessible or Use Pre-signed URLs**
3. **Download in App Using boto3**

## Recommended: Use Smaller Model

The `chilli_disease_detection_model_final.h5` (104MB) is smaller. Consider:

1. **Model Quantization**
   ```python
   import tensorflow as tf
   
   # Convert to TFLite (much smaller)
   converter = tf.lite.TFLiteConverter.from_keras_model(model)
   converter.optimizations = [tf.lite.Optimize.DEFAULT]
   tflite_model = converter.convert()
   
   with open('model.tflite', 'wb') as f:
       f.write(tflite_model)
   ```

2. **Use TFLite in Production**
   - Much smaller file size (can be < 25MB)
   - Faster inference
   - Better for serverless environments

## Implementation Steps

1. Choose hosting method (Hugging Face recommended)
2. Upload your model
3. Modify app.py to download model at startup
4. Add caching to avoid re-downloading
5. Deploy to Vercel

Would you like me to implement any of these solutions?
