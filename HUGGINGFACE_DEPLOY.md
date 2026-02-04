# 🚀 Hugging Face Deployment Guide

## Prerequisites
- Hugging Face account (sign up at https://huggingface.co/)
- Git installed on your machine
- Git LFS (Large File Storage) installed

## Step 1: Install Git LFS
Git LFS is required for large model files.

**Windows:**
```bash
git lfs install
```

## Step 2: Create a New Space on Hugging Face

1. Go to https://huggingface.co/new-space
2. Fill in the details:
   - **Space name**: `chilli-care` (or your preferred name)
   - **License**: MIT
   - **Select SDK**: Docker
   - **Space hardware**: CPU basic (free tier) or upgrade if needed
3. Click "Create Space"

## Step 3: Clone Your New Space

After creating the space, copy the clone URL and run:

```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/chilli-care
cd chilli-care
```

## Step 4: Copy Project Files

Copy all necessary files from your Chilli Care project to the cloned space directory:

```bash
# From your Chilli Care directory
cp -r * /path/to/chilli-care/
```

Or manually copy these essential files:
- `app.py`
- `requirements.txt`
- `Dockerfile`
- `.dockerignore`
- `README.md`
- `class_names.json`
- `best_chilli_disease_model.h5`
- `templates/` folder
- `static/` folder (excluding images if you want)

## Step 5: Track Large Files with Git LFS

Track your model file with Git LFS (required for files > 10MB):

```bash
git lfs track "*.h5"
git lfs track "*.keras"
git add .gitattributes
```

## Step 6: Commit and Push to Hugging Face

```bash
git add .
git commit -m "Initial deployment of Chilli Care Disease Detection"
git push
```

## Step 7: Wait for Deployment

- Go to your space URL: `https://huggingface.co/spaces/YOUR_USERNAME/chilli-care`
- The space will automatically build and deploy (this may take 5-10 minutes)
- Watch the build logs in the "Logs" tab

## Step 8: Test Your Deployment

Once deployed, your app will be available at:
```
https://YOUR_USERNAME-chilli-care.hf.space
```

## Troubleshooting

### Build Fails
- Check the logs in the "Logs" tab
- Ensure all dependencies are in `requirements.txt`
- Verify Dockerfile syntax

### Model Not Loading
- Ensure model file is tracked with Git LFS
- Check file path in `app.py` matches the actual filename
- Verify `class_names.json` exists

### Out of Memory
- Upgrade to a better hardware tier in Space settings
- Consider using a smaller model
- Reduce the number of gunicorn workers in Dockerfile

### Port Issues
- Hugging Face Spaces use port 7860 by default (already configured in Dockerfile)

## Alternative: Quick Deploy from GitHub

If your code is already on GitHub:

1. Create a new Hugging Face Space
2. In Space settings, enable "Link to GitHub"
3. Connect your GitHub repository
4. Hugging Face will auto-sync and deploy

## Updating Your Deployment

To update your deployed app:

```bash
# Make changes to your code
git add .
git commit -m "Update: description of changes"
git push
```

The space will automatically rebuild and redeploy.

## Cost Considerations

- **Free tier**: CPU basic (sufficient for testing)
- **Paid tiers**: Available for better performance
  - CPU upgrade: Faster processing
  - GPU: For heavy ML workloads (probably not needed for inference)

## Public vs Private

- **Public spaces** (free): Anyone can access your app
- **Private spaces** (paid): Restricted access

You can change this in Space settings.

## Environment Variables (Optional)

If you need to add secrets or API keys:

1. Go to Space Settings
2. Click "Variables and secrets"
3. Add your environment variables

## Next Steps

After successful deployment:
1. Test all features thoroughly
2. Share your space URL
3. Monitor usage in the Space analytics
4. Consider adding a demo video or images to README

## Support

- Hugging Face Docs: https://huggingface.co/docs/hub/spaces
- Community Forum: https://discuss.huggingface.co/
- Discord: https://hf.co/join/discord
