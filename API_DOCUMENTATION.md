# API DOCUMENTATION

## Base URL
```
https://YOUR-DEPLOYED-URL.onrender.com
```

## Authentication
All requests to `/detect` endpoint require API key authentication.

**Header:**
```
x-api-key: your-api-key-here
```

**Valid Test Keys:**
- `test-key-123`
- `guvi-api-key-2024`
- `demo-key-456`

## Endpoints

### 1. Health Check
Check if the API is running.

**Endpoint:** `GET /health`

**Authentication:** Not required

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-30T12:34:56.789Z"
}
```

**Status Codes:**
- `200` - Service is healthy

---

### 2. Service Information
Get information about the API service.

**Endpoint:** `GET /`

**Authentication:** Not required

**Response:**
```json
{
  "service": "AI Voice Detection API",
  "status": "online",
  "version": "1.0.0",
  "supported_languages": ["tamil", "english", "hindi", "malayalam", "telugu"]
}
```

**Status Codes:**
- `200` - Success

---

### 3. Voice Detection
Detect if a voice sample is AI-generated or human.

**Endpoint:** `POST /detect`

**Authentication:** Required (`x-api-key` header)

**Request Body:**
```json
{
  "language": "english",
  "audio_format": "mp3",
  "audio_base64": "<Base64 encoded MP3 audio>"
}
```

**Request Fields:**

| Field | Type | Required | Description | Valid Values |
|-------|------|----------|-------------|--------------|
| `language` | string | Yes | Language of the audio | `tamil`, `english`, `hindi`, `malayalam`, `telugu` |
| `audio_format` | string | Yes | Audio file format | `mp3` |
| `audio_base64` | string | Yes | Base64 encoded audio data | Valid Base64 string |

**Success Response (200):**
```json
{
  "status": "success",
  "classification": "AI_GENERATED",
  "confidence": 0.8542,
  "language": "english",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Always "success" for successful requests |
| `classification` | string | "AI_GENERATED" or "HUMAN" |
| `confidence` | float | Confidence score between 0.00 and 1.00 |
| `language` | string | Language of the processed audio |
| `request_id` | string | Unique identifier for the request (UUID) |

**Error Response (4xx/5xx):**
```json
{
  "status": "error",
  "error_code": "INVALID_API_KEY",
  "message": "Invalid or missing API key"
}
```

**Error Codes:**

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_API_KEY` | 401 | API key is missing or invalid |
| `INVALID_AUDIO` | 400 | Audio data is corrupted or invalid |
| `BAD_REQUEST` | 400 | Request validation failed |
| `INTERNAL_ERROR` | 500 | Server error during processing |

---

## Request Examples

### cURL Example
```bash
curl -X POST https://YOUR-API-URL/detect \
  -H "Content-Type: application/json" \
  -H "x-api-key: test-key-123" \
  -d '{
    "language": "english",
    "audio_format": "mp3",
    "audio_base64": "//uQxAAAAAAAAAAAAAAA..."
  }'
```

### Python Example
```python
import requests
import base64

# Read audio file
with open("audio.mp3", "rb") as f:
    audio_data = f.read()

# Encode to Base64
audio_base64 = base64.b64encode(audio_data).decode('utf-8')

# Make request
response = requests.post(
    "https://YOUR-API-URL/detect",
    headers={
        "Content-Type": "application/json",
        "x-api-key": "test-key-123"
    },
    json={
        "language": "english",
        "audio_format": "mp3",
        "audio_base64": audio_base64
    }
)

# Print result
print(response.json())
```

### JavaScript Example
```javascript
const fs = require('fs');
const axios = require('axios');

// Read and encode audio
const audioBuffer = fs.readFileSync('audio.mp3');
const audioBase64 = audioBuffer.toString('base64');

// Make request
axios.post('https://YOUR-API-URL/detect', {
  language: 'english',
  audio_format: 'mp3',
  audio_base64: audioBase64
}, {
  headers: {
    'Content-Type': 'application/json',
    'x-api-key': 'test-key-123'
  }
})
.then(response => {
  console.log(response.data);
})
.catch(error => {
  console.error(error.response.data);
});
```

---

## Rate Limits

**Free Tier (Render.com/Railway):**
- No hard rate limits
- Requests may be slower during cold starts
- Recommended: < 10 concurrent requests

**Best Practices:**
- Implement request retry logic
- Handle 5xx errors gracefully
- Cache results when appropriate

---

## Audio Requirements

**Format:** MP3

**Encoding:** Base64

**Minimum Duration:** 0.5 seconds

**Maximum Size:** 10 MB recommended

**Sample Rate:** Any (will be resampled to 16kHz)

**Channels:** Mono or Stereo (will be converted to mono)

---

## Response Times

**Average Response Time:**
- Cold start: 30-60 seconds (first request after idle)
- Warm requests: 1-3 seconds
- Complex audio: 3-5 seconds

**Timeout Recommendations:**
- Set HTTP timeout to 60 seconds
- Implement retry logic for timeouts

---

## Error Handling Best Practices

```python
import requests
from requests.exceptions import Timeout, RequestException

def detect_voice(audio_base64, language="english"):
    url = "https://YOUR-API-URL/detect"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": "test-key-123"
    }
    payload = {
        "language": language,
        "audio_format": "mp3",
        "audio_base64": audio_base64
    }
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print("Authentication failed: Invalid API key")
        elif response.status_code == 400:
            error = response.json()
            print(f"Bad request: {error['message']}")
        else:
            print(f"Server error: {response.status_code}")
            
    except Timeout:
        print("Request timed out. API might be cold starting.")
    except RequestException as e:
        print(f"Request failed: {e}")
    
    return None
```

---

## Testing Your Integration

Use the official GUVI Endpoint Tester:
1. Enter your API endpoint: `https://YOUR-URL/detect`
2. Enter API key: `test-key-123`
3. Select language: Any supported language
4. Upload MP3 file or provide Base64
5. Click "Test Endpoint"

Expected result:
- ✅ Status 200
- ✅ Valid JSON response
- ✅ Classification: AI_GENERATED or HUMAN
- ✅ Confidence: 0.00 to 1.00
- ✅ Request ID present

---

## Support

**Documentation:**
- README.md - Overview
- QUICK_START.md - Quick deployment guide
- DEPLOYMENT_RENDER.md - Render deployment
- DEPLOYMENT_RAILWAY.md - Railway deployment

**Common Issues:**
- API key not working → Check environment variable `API_KEYS`
- Timeout errors → API is cold starting, retry after 60s
- Invalid audio → Ensure valid MP3 format and Base64 encoding
- 500 errors → Check server logs in Render/Railway dashboard

---

## API Versioning

Current Version: **1.0.0**

Version is included in root endpoint response:
```
GET / → "version": "1.0.0"
```

---

## Changelog

**v1.0.0 (2026-01-30)**
- Initial release
- Multi-language support (5 languages)
- AI voice detection with confidence scoring
- API key authentication
- Production-ready deployment
