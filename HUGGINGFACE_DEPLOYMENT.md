# 🤗 HuggingFace Spaces Deployment Guide

## Quick Deployment Steps

### Method 1: Git Clone (Recommended)

1. **Create New Space**
   - Go to [huggingface.co/new-space](https://huggingface.co/new-space)
   - Name: `tender-digest-ai`
   - SDK: **Streamlit**
   - Hardware: **CPU Basic** (free) or **GPU** for better performance

2. **Clone Your Space Repository**
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/tender-digest-ai
   cd tender-digest-ai
   ```

3. **Copy Files from This Project**
   ```bash
   # Copy main application files
   cp /path/to/Tender-Digest-AI/app.py .
   cp /path/to/Tender-Digest-AI/requirements_hf.txt requirements.txt
   cp /path/to/Tender-Digest-AI/README_HF.md README.md
   ```

4. **Create README.md Header**
   ```yaml
   ---
   title: Tender Digest AI
   emoji: 📊
   colorFrom: blue
   colorTo: purple
   sdk: streamlit
   sdk_version: 1.28.0
   app_file: app.py
   pinned: false
   license: apache-2.0
   ---
   ```

5. **Push to HuggingFace**
   ```bash
   git add .
   git commit -m "Initial deployment of Tender Digest AI"
   git push
   ```

### Method 2: File Upload

1. **Create Space** (same as above)
2. **Upload Files** directly through HuggingFace interface:
   - `app.py` (main application)
   - `requirements.txt` (use requirements_hf.txt contents)
   - `README.md` (with proper header)

## Required Files for HuggingFace Spaces

### 1. app.py
Your main Streamlit application (already ready)

### 2. requirements.txt
```
streamlit>=1.28.0
langchain==0.1.0
langchain-core==0.1.23
langchain-community==0.0.20
langchain-huggingface==0.0.3
transformers==4.36.0
sentence-transformers==2.2.2
huggingface-hub>=0.19.0
PyPDF2==3.0.1
faiss-cpu==1.7.4
numpy==1.24.3
```

### 3. README.md
Must start with YAML frontmatter (see README_HF.md)

## Hardware Options

### CPU Basic (Free)
- ✅ Free forever
- ✅ Good for lightweight analysis
- ⚠️ Slower model loading (2-3 minutes)
- ⚠️ May timeout on large documents

### CPU Upgrade ($0.05/hour)
- ✅ 4x faster performance
- ✅ Better memory handling
- ✅ Handles larger documents
- 💰 ~$36/month if running 24/7

### GPU T4 Small ($0.60/hour)
- ✅ Very fast model loading
- ✅ Best for AI-heavy workloads
- ✅ Can handle multiple users
- 💰 ~$432/month if running 24/7

## Optimization Tips

### 1. Model Caching
```python
@st.cache_resource
def load_models():
    # Models cached between sessions
    pass
```

### 2. Secrets Management
Add HuggingFace API tokens in Space settings:
- Settings → Repository secrets
- Add `HF_TOKEN` for better rate limits

### 3. Memory Management
- Use CPU-optimized models
- Implement lazy loading
- Clear cache when needed

## Troubleshooting

### Build Errors
- Check requirements.txt formatting
- Ensure compatible package versions
- Remove conflicting dependencies

### Runtime Errors
- Check HuggingFace model availability
- Verify internet connectivity for model downloads
- Monitor memory usage

### Performance Issues
- Upgrade to paid hardware
- Optimize model loading
- Implement progressive loading

## Benefits of HuggingFace Spaces

✅ **AI-Optimized**: Perfect for ML/AI applications
✅ **Community**: Easy sharing and discovery
✅ **GPU Access**: Available with paid plans
✅ **Model Hub**: Direct access to HF models
✅ **Version Control**: Git-based deployment
✅ **Custom Domains**: Available for Pro users

## Post-Deployment

After successful deployment:

1. **Test thoroughly** with various PDF files
2. **Monitor performance** and upgrade hardware if needed
3. **Share your Space** with the community
4. **Add to your portfolio** - great showcase piece!

Your app will be live at:
`https://huggingface.co/spaces/YOUR_USERNAME/tender-digest-ai`

## Need Help?

- HuggingFace Spaces docs: [huggingface.co/docs/hub/spaces](https://huggingface.co/docs/hub/spaces)
- Community forum: [discuss.huggingface.co](https://discuss.huggingface.co)
- Discord: HuggingFace community server