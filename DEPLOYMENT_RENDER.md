# 🚀 Deployment Guide - Render.com

## Step 1: Prepare Repository

1. Initialize Git repository:
```bash
cd "d:\CS\Guvi Hackathon"
git init
git add .
git commit -m "Initial commit: AI Voice Detection API"
```

2. Create GitHub repository and push:
```bash
git remote add origin https://github.com/YOUR_USERNAME/ai-voice-detection.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy on Render

1. **Sign up/Login**: Go to [render.com](https://render.com)

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `ai-voice-detection` repository

3. **Configure Service**:
   - **Name**: `ai-voice-detection-api`
   - **Region**: Oregon (US West)
   - **Branch**: `main`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

4. **Environment Variables**:
   Click "Advanced" → "Add Environment Variable":
   - Key: `API_KEYS`
   - Value: `test-key-123,guvi-api-key-2024,your-custom-key`

5. **Health Check**:
   - Path: `/health`
   - Enable auto-deploy from GitHub

6. **Deploy**: Click "Create Web Service"

## Step 3: Get Your Public URL

After deployment completes (5-10 minutes):
- Your API will be live at: `https://ai-voice-detection-api.onrender.com`
- Test health: `https://ai-voice-detection-api.onrender.com/health`

## Step 4: Test Your Endpoint

```bash
curl -X POST https://ai-voice-detection-api.onrender.com/detect \
  -H "Content-Type: application/json" \
  -H "x-api-key: test-key-123" \
  -d '{
    "language": "english",
    "audio_format": "mp3",
    "audio_base64": "YOUR_BASE64_AUDIO_HERE"
  }'
```

## Step 5: Submit to GUVI Endpoint Tester

Use these details in the tester:
- **Endpoint URL**: `https://ai-voice-detection-api.onrender.com/detect`
- **API Key**: `test-key-123` (or your custom key)
- **Method**: POST
- **Language**: Any of [tamil, english, hindi, malayalam, telugu]

## 🔧 Troubleshooting

### Build Fails
- Check `requirements.txt` is present
- Ensure Python version is specified in `runtime.txt`
- Check logs in Render dashboard

### API Returns 500
- Check logs for errors
- Verify librosa dependencies installed correctly
- Test locally first: `uvicorn main:app --reload`

### Slow First Request
- Free tier sleeps after inactivity
- First request may take 30-60 seconds
- Use a cron job to keep it awake:
  ```bash
  */10 * * * * curl https://ai-voice-detection-api.onrender.com/health
  ```

## 📊 Monitoring

Render provides:
- Real-time logs
- Metrics dashboard
- Auto-restart on crashes
- HTTPS by default

## 🔄 Updates

To update your API:
```bash
git add .
git commit -m "Update: description"
git push
```

Render will auto-deploy within minutes.

---

**🎉 Your API is now live and ready for evaluation!**
