"""
Test script for AI Voice Detection API
"""

import requests
import base64
import json
from pathlib import Path


def test_api(endpoint_url: str, api_key: str, audio_file_path: str = None, language: str = "english"):
    """
    Test the AI Voice Detection API
    
    Args:
        endpoint_url: Base URL of the API
        api_key: API key for authentication
        audio_file_path: Path to MP3 file (optional, will create test data if not provided)
        language: Language of the audio sample
    """
    
    # If no audio file provided, create minimal test data
    if audio_file_path and Path(audio_file_path).exists():
        with open(audio_file_path, 'rb') as f:
            audio_data = f.read()
    else:
        # Create minimal MP3-like data for testing (not real MP3, just for structure test)
        print("Warning: No audio file provided, using minimal test data")
        audio_data = b'\xFF\xFB' + b'\x00' * 5000  # MP3 frame header + data
    
    # Encode to base64
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    # Prepare request
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }
    
    payload = {
        "language": language,
        "audio_format": "mp3",
        "audio_base64": audio_base64
    }
    
    print(f"\n🧪 Testing API: {endpoint_url}")
    print(f"📍 Language: {language}")
    print(f"🔑 API Key: {api_key[:10]}...")
    print(f"📦 Audio Size: {len(audio_data)} bytes")
    print(f"📊 Base64 Size: {len(audio_base64)} chars")
    
    try:
        # Test health endpoint
        print("\n✅ Testing /health endpoint...")
        health_response = requests.get(f"{endpoint_url}/health")
        print(f"Status: {health_response.status_code}")
        print(f"Response: {health_response.json()}")
        
        # Test detection endpoint
        print("\n✅ Testing /detect endpoint...")
        response = requests.post(
            f"{endpoint_url}/detect",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📄 Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ SUCCESS!")
            print(f"🎯 Classification: {result['classification']}")
            print(f"📈 Confidence: {result['confidence']:.4f}")
            print(f"🆔 Request ID: {result['request_id']}")
            return True
        else:
            print(f"\n❌ FAILED with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False


def test_authentication(endpoint_url: str):
    """Test API key authentication"""
    print("\n🔐 Testing Authentication...")
    
    # Test with no API key
    print("\n1️⃣ Testing without API key...")
    response = requests.post(
        f"{endpoint_url}/detect",
        json={
            "language": "english",
            "audio_format": "mp3",
            "audio_base64": base64.b64encode(b'\xFF\xFB' + b'\x00' * 5000).decode()
        }
    )
    
    if response.status_code == 401:
        print("✅ Correctly rejected request without API key")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
    
    # Test with invalid API key
    print("\n2️⃣ Testing with invalid API key...")
    response = requests.post(
        f"{endpoint_url}/detect",
        headers={"x-api-key": "invalid-key-999"},
        json={
            "language": "english",
            "audio_format": "mp3",
            "audio_base64": base64.b64encode(b'\xFF\xFB' + b'\x00' * 5000).decode()
        }
    )
    
    if response.status_code == 401:
        print("✅ Correctly rejected request with invalid API key")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Unexpected status code: {response.status_code}")


if __name__ == "__main__":
    # Configuration
    ENDPOINT_URL = "http://localhost:8000"  # Change to deployed URL
    API_KEY = "test-key-123"
    
    # Run tests
    print("=" * 60)
    print("🚀 AI Voice Detection API - Test Suite")
    print("=" * 60)
    
    # Test authentication
    test_authentication(ENDPOINT_URL)
    
    # Test with different languages
    languages = ["english", "tamil", "hindi", "malayalam", "telugu"]
    
    for lang in languages:
        print(f"\n{'=' * 60}")
        test_api(ENDPOINT_URL, API_KEY, language=lang)
    
    print(f"\n{'=' * 60}")
    print("✅ Test suite completed!")
    print("=" * 60)
