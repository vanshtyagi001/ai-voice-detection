# AI-Generated Voice Detection API

Production-ready REST API for detecting AI-generated voices in multiple languages.

## 🎯 Features

- **Multi-language Support**: Tamil, English, Hindi, Malayalam, Telugu
- **AI Detection**: Advanced audio feature extraction and ML-based classification
- **API Key Authentication**: Secure x-api-key header authentication
- **Production Ready**: Fast, stable, and scalable
- **Standards Compliant**: Follows the official endpoint specification

## 🚀 API Endpoint

**Base URL**: `https://your-deployment-url.onrender.com`

### Authentication

All requests require an API key in the header:
```
x-api-key: your-api-key-here
```

### Request Format

**POST /detect**

```json
{
  "language": "english",
  "audio_format": "mp3",
  "audio_base64": "<Base64 encoded MP3 file>"
}
```

### Response Format

**Success:**
```json
{
  "status": "success",
  "classification": "AI_GENERATED",
  "confidence": 0.8542,
  "language": "english",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Error:**
```json
{
  "status": "error",
  "error_code": "INVALID_API_KEY",
  "message": "Invalid or missing API key"
}
```

## 🛠️ Technology Stack

- **FastAPI**: High-performance async API framework
- **Librosa**: Advanced audio processing and feature extraction
- **NumPy/SciPy**: Scientific computing for signal processing
- **Uvicorn**: ASGI server for production deployment

## 🧠 Detection Algorithm

The system uses multiple detection strategies:

1. **MFCC Analysis**: Mel-frequency cepstral coefficients for spectral envelope
2. **Spectral Features**: Centroid, rolloff, bandwidth, contrast, flatness
3. **Phase Coherence**: Detects AI-generated phase artifacts
4. **Pitch Analysis**: Naturalness and stability of pitch patterns
5. **Temporal Statistics**: Time-domain anomaly detection
6. **Harmonic Analysis**: Harmonic-percussive source separation

## 📦 Local Development

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn main:app --reload --port 8000
```

### Test Request

```bash
curl -X POST http://localhost:8000/detect \
  -H "Content-Type: application/json" \
  -H "x-api-key: test-key-123" \
  -d '{
    "language": "english",
    "audio_format": "mp3",
    "audio_base64": "<your_base64_encoded_mp3>"
  }'
```

## 🌐 Deployment

### Render.com (Recommended)

1. Push code to GitHub
2. Connect repository to Render
3. Deploy as Web Service
4. Set environment variable `API_KEYS`

### Railway.app

```bash
railway login
railway init
railway up
```

## 🔑 API Keys

Configure valid API keys via environment variable:
```
API_KEYS=key1,key2,key3
```

Default keys for testing:
- `test-key-123`
- `guvi-api-key-2024`
- `demo-key-456`

## 📊 Performance

- **Response Time**: < 2 seconds average
- **Accuracy**: Multi-feature ensemble approach
- **Stability**: Error handling and graceful degradation
- **Scalability**: Async processing with concurrent request support

## 🧪 Testing

Health check:
```bash
curl https://your-deployment-url.onrender.com/health
```

Service info:
```bash
curl https://your-deployment-url.onrender.com/
```

## 📝 Error Codes

| Code | Description |
|------|-------------|
| `INVALID_API_KEY` | Missing or invalid API key |
| `INVALID_AUDIO` | Audio decoding or validation failed |
| `BAD_REQUEST` | Malformed request or validation error |
| `INTERNAL_ERROR` | Server error during processing |

## 🎓 Supported Languages

- `tamil` - Tamil
- `english` - English
- `hindi` - Hindi
- `malayalam` - Malayalam
- `telugu` - Telugu

## 📄 License

MIT License

## 🤝 Contributing

This is a competition submission for GUVI AI Hackathon.

---

**Built with ❤️ for GUVI Hackathon 2026**
