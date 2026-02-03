# 🎯 QUICK START GUIDE

## ✅ What Has Been Built

A complete production-ready AI-Generated Voice Detection API with:

1. ✅ **FastAPI Server** - High-performance REST API
2. ✅ **Audio Processing** - Advanced feature extraction using librosa
3. ✅ **AI Detection** - Multi-strategy ML-based voice classification
4. ✅ **API Key Auth** - Secure x-api-key header authentication
5. ✅ **Multi-language** - Tamil, English, Hindi, Malayalam, Telugu
6. ✅ **Error Handling** - Comprehensive validation and error responses
7. ✅ **Deployment Config** - Ready for Render, Railway, or any cloud platform

## 🚀 DEPLOY NOW (Choose One)

### Option 1: Render.com (RECOMMENDED - Free, Easy)

1. **Push to GitHub**:
```bash
cd "d:\CS\Guvi Hackathon"
git init
git add .
git commit -m "AI Voice Detection API"
git remote add origin YOUR_GITHUB_URL
git push -u origin main
```

2. **Deploy on Render**:
   - Go to https://render.com
   - Sign up/Login with GitHub
   - Click "New +" → "Web Service"
   - Connect your repo
   - Settings:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
     - **Environment Variable**: 
       - Key: `API_KEYS`
       - Value: `test-key-123,guvi-api-key-2024`
   - Click "Create Web Service"

3. **Get Your URL**: 
   - After 5-10 minutes: `https://YOUR-APP.onrender.com`

### Option 2: Railway.app (Fast Deployment)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
cd "d:\CS\Guvi Hackathon"
railway login
railway init
railway variables set API_KEYS="test-key-123,guvi-api-key-2024"
railway up
railway domain
```

Your API will be live at: `https://YOUR-APP.railway.app`

## 🧪 TEST YOUR DEPLOYED API

### 1. Health Check
```bash
curl https://YOUR-DEPLOYED-URL/health
```

### 2. Test Detection
```bash
curl -X POST https://YOUR-DEPLOYED-URL/detect \
  -H "Content-Type: application/json" \
  -H "x-api-key: test-key-123" \
  -d '{
    "language": "english",
    "audio_format": "mp3",
    "audio_base64": "YOUR_BASE64_AUDIO_HERE"
  }'
```

### 3. Use Python Test Script
```bash
python test_api.py
```
Edit the `ENDPOINT_URL` in test_api.py to your deployed URL.

## 📋 FOR GUVI ENDPOINT TESTER

Submit these details:

- **Endpoint URL**: `https://YOUR-DEPLOYED-URL/detect`
- **HTTP Method**: POST
- **API Key Header**: `x-api-key`
- **API Key Value**: `test-key-123` (or your custom key)
- **Supported Languages**: tamil, english, hindi, malayalam, telugu
- **Audio Format**: mp3 (Base64 encoded)

### Expected Response Format
```json
{
  "status": "success",
  "classification": "AI_GENERATED",
  "confidence": 0.8542,
  "language": "english",
  "request_id": "uuid-here"
}
```

## 🔑 API Keys

Default test keys (change in production):
- `test-key-123`
- `guvi-api-key-2024`

To add more keys, update environment variable:
```
API_KEYS=key1,key2,key3
```

## 📁 Project Structure

```
d:\CS\Guvi Hackathon\
├── main.py                    # FastAPI application & routes
├── detector.py                # AI detection engine
├── requirements.txt           # Python dependencies
├── Procfile                   # Deployment start command
├── render.yaml               # Render.com configuration
├── runtime.txt               # Python version specification
├── test_api.py               # Comprehensive test suite
├── quick_test.py             # Quick local test
├── README.md                 # Full documentation
├── DEPLOYMENT_RENDER.md      # Render deployment guide
├── DEPLOYMENT_RAILWAY.md     # Railway deployment guide
├── QUICK_START.md           # This file
└── .gitignore               # Git ignore rules
```

## 🧠 How It Works

### Detection Algorithm
The system analyzes audio using multiple features:
1. **MFCC** - Spectral envelope analysis
2. **Spectral Features** - Centroid, rolloff, bandwidth, contrast
3. **Phase Coherence** - Detects AI synthesis artifacts
4. **Pitch Analysis** - Naturalness and stability
5. **Temporal Statistics** - Time-domain patterns
6. **Harmonic Analysis** - Harmonic-percussive separation

### Multi-Strategy Scoring
- Each strategy contributes to an AI score (0-1)
- Confidence calculated from detection clarity
- Final classification based on threshold (0.5)

## 🔧 Local Testing

### Start Server Locally
```bash
cd "d:\CS\Guvi Hackathon"
python -m uvicorn main:app --reload --port 8000
```

### Access API
- Health: http://localhost:8000/health
- Docs: http://localhost:8000/docs (Interactive API docs)
- Detection: POST http://localhost:8000/detect

## 📊 API Specification

### Request Format
```json
{
  "language": "english",          // Required: tamil|english|hindi|malayalam|telugu
  "audio_format": "mp3",          // Required: currently only "mp3"
  "audio_base64": "Base64String"  // Required: Base64 encoded MP3
}
```

### Success Response
```json
{
  "status": "success",
  "classification": "AI_GENERATED",  // or "HUMAN"
  "confidence": 0.8542,              // 0.00 to 1.00
  "language": "english",
  "request_id": "uuid"
}
```

### Error Response
```json
{
  "status": "error",
  "error_code": "INVALID_API_KEY",  // or INVALID_AUDIO, BAD_REQUEST, INTERNAL_ERROR
  "message": "Descriptive error message"
}
```

## 🎯 Next Steps

1. ✅ **Deploy** using Render or Railway (see above)
2. ✅ **Test** using curl or the test scripts
3. ✅ **Submit** to GUVI Endpoint Tester
4. ✅ **Monitor** logs and performance
5. ✅ **Pass** automated evaluation!

## 🐛 Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### "Port already in use"
```bash
# Change port in command
uvicorn main:app --port 8001
```

### "Audio processing failed"
- Ensure audio is valid MP3 format
- Check Base64 encoding is correct
- Verify audio is at least 0.5 seconds long

### Slow response on free tier
- First request after idle may take 30-60s
- Subsequent requests are fast
- Use a keep-alive ping if needed

## 📞 Support

For deployment issues:
- Render: https://render.com/docs
- Railway: https://docs.railway.app

---

## ✅ SUMMARY

**Your API is ready for deployment!**

All code is production-ready, tested, and follows the exact specification. Simply:
1. Deploy to Render/Railway (10 minutes)
2. Get your public URL
3. Submit to the endpoint tester
4. Pass evaluation! 🎉

**Built for GUVI AI Hackathon 2026** 🚀
