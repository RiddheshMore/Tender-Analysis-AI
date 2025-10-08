# 🚀 Deployment Guide for Tender Digest AI

This guide will help you deploy the Tender Digest AI application on various free hosting platforms.

## 📦 Available Versions

1. **`app.py`** - Full-featured version with AI models (requires more resources)
2. **`app_deploy.py`** - Lightweight version optimized for free hosting (recommended for deployment)

## 🎯 Recommended Platform: Streamlit Cloud (Free)

### Prerequisites
- GitHub account
- Your code pushed to a GitHub repository

### Step-by-Step Deployment on Streamlit Cloud

1. **Visit Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

2. **Create New App**
   - Click "New app"
   - Select your repository: `Tender-Analysis-AI`
   - Set branch: `main`
   - Set main file path: `app_deploy.py`
   - Click "Deploy!"

3. **Configure App Settings**
   - App name: `tender-digest-ai`
   - URL will be: `https://tender-digest-ai.streamlit.app`

4. **Wait for Deployment**
   - Initial deployment takes 2-5 minutes
   - Your app will be live at the generated URL

### Configuration Files for Streamlit Cloud
- `.streamlit/secrets.toml` - Already created for secrets management
- `requirements_deploy.txt` - Lightweight dependencies

## 🤗 Alternative: Hugging Face Spaces

### Step-by-Step Deployment on HF Spaces

1. **Create New Space**
   - Go to [huggingface.co/new-space](https://huggingface.co/new-space)
   - Space name: `tender-digest-ai`
   - License: Apache 2.0
   - SDK: Streamlit
   - Hardware: CPU Basic (free)

2. **Upload Files**
   - Upload `app_deploy.py` as `app.py` (HF Spaces looks for app.py)
   - Upload `requirements_deploy.txt` as `requirements.txt`
   - Upload any additional files if needed

3. **Space Configuration**
   - The space will automatically deploy
   - URL will be: `https://huggingface.co/spaces/YOUR_USERNAME/tender-digest-ai`

## 🔧 Files Needed for Deployment

### Required Files:
```
Tender-Analysis-AI/
├── app_deploy.py (main app file)
├── requirements_deploy.txt (dependencies)
├── README.md (project documentation)
└── .streamlit/
    └── secrets.toml (configuration)
```

### File Configurations:

#### For Streamlit Cloud:
- Main file: `app_deploy.py`
- Requirements: `requirements_deploy.txt`

#### For Hugging Face Spaces:
- Rename `app_deploy.py` to `app.py`
- Rename `requirements_deploy.txt` to `requirements.txt`

## 🚀 Quick Deployment Commands

If you haven't pushed to GitHub yet, run these commands in your terminal:

```bash
# Navigate to project directory
cd /home/ritz/Desktop/langchain_models/Tender-Digest-AI

# Add all files
git add .

# Commit changes
git commit -m "Add deployment-optimized version and configuration files"

# Push to GitHub
git push origin main
```

## 🔍 Performance Optimization

The deployment version (`app_deploy.py`) includes:

- ✅ **Rule-based analysis** instead of heavy AI models
- ✅ **Minimal dependencies** (only Streamlit + PyPDF2)
- ✅ **Fast processing** suitable for free hosting
- ✅ **Memory efficient** operations
- ✅ **Quick startup time**

## 📊 Expected Performance

- **Startup time**: < 30 seconds
- **Analysis time**: 2-5 seconds per document
- **Memory usage**: < 512 MB
- **Suitable for**: Up to 10 concurrent users

## 🆓 Free Hosting Limitations

### Streamlit Cloud (Free Tier):
- ✅ 1 GB RAM
- ✅ 1 CPU core
- ✅ Unlimited public apps
- ✅ Custom domains
- ⚠️ Apps sleep after 7 days of inactivity

### Hugging Face Spaces (Free Tier):
- ✅ 16 GB RAM
- ✅ 2 CPU cores  
- ✅ Persistent storage
- ✅ Public spaces
- ⚠️ May have queue during high usage

## 🔧 Troubleshooting

### Common Issues:

1. **App won't start**
   - Check `requirements_deploy.txt` for correct package names
   - Ensure `app_deploy.py` has no syntax errors

2. **Out of memory errors**
   - The lightweight version should avoid this
   - If it occurs, further reduce dependencies

3. **Slow performance**
   - The deployment version is optimized for speed
   - Consider reducing file size limits if needed

4. **Module import errors**
   - Verify all imports in `requirements_deploy.txt`
   - Check that file names match exactly

## 📞 Support

If you encounter issues:
1. Check the deployment platform's logs
2. Verify all files are uploaded correctly
3. Ensure requirements.txt has correct package versions
4. Test locally first: `streamlit run app_deploy.py`

## 🎉 Success Checklist

After deployment, verify:
- [ ] App loads without errors
- [ ] File upload works
- [ ] PDF analysis completes
- [ ] Results display correctly
- [ ] Download functionality works
- [ ] App is accessible via public URL

Your Tender Digest AI app should now be live and accessible to users worldwide! 🌍