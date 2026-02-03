# 🚀 Deployment Guide - Railway.app

## Step 1: Install Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Or use PowerShell
iwr https://railway.app/install.ps1 | iex
```

## Step 2: Login to Railway

```bash
railway login
```

## Step 3: Initialize Project

```bash
cd "d:\CS\Guvi Hackathon"
railway init
```

Select:
- Create a new project
- Name: `ai-voice-detection-api`

## Step 4: Configure Environment Variables

```bash
railway variables set API_KEYS="test-key-123,guvi-api-key-2024,your-custom-key"
```

## Step 5: Deploy

```bash
railway up
```

Railway will:
1. Detect Python project
2. Install dependencies from `requirements.txt`
3. Start with command from `Procfile`
4. Provide public URL

## Step 6: Get Your Public URL

```bash
railway domain
```

Or in Railway dashboard:
1. Go to your project
2. Click "Settings"
3. Generate domain: `your-app.railway.app`

## Step 7: Monitor Deployment

```bash
# View logs
railway logs

# Check status
railway status

# Open in browser
railway open
```

## Alternative: GitHub Integration

1. Push code to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO
git push -u origin main
```

2. In Railway dashboard:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Configure variables
   - Deploy

## 🧪 Testing

```bash
# Health check
curl https://your-app.railway.app/health

# Test detection
curl -X POST https://your-app.railway.app/detect \
  -H "Content-Type: application/json" \
  -H "x-api-key: test-key-123" \
  -d '{
    "language": "english",
    "audio_format": "mp3",
    "audio_base64": "BASE64_AUDIO"
  }'
```

## 🔧 Configuration

Railway automatically detects:
- `requirements.txt` for dependencies
- `Procfile` for start command
- `runtime.txt` for Python version

## 💰 Pricing

- $5/month hobby plan includes:
  - 512 MB RAM
  - Shared CPU
  - 100 GB bandwidth
  - Perfect for this API

## 🔄 Updates

```bash
# Make changes
git add .
git commit -m "Update"
git push

# Or direct deploy
railway up
```

## 📊 Monitoring

```bash
# Real-time logs
railway logs --follow

# Metrics
railway metrics
```

---

**🎉 Your API is now live on Railway!**
