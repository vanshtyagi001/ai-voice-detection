#!/usr/bin/env python3
"""
Simple test script for the AI Voice Detection API
"""
import requests
import base64

# Test the API
url = "http://127.0.0.1:8000"

print("🧪 Testing AI Voice Detection API")
print("=" * 50)

# Test 1: Health Check
print("\n1️⃣ Testing Health Check...")
try:
    response = requests.get(f"{url}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Service Info
print("\n2️⃣ Testing Service Info...")
try:
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Detection endpoint (without API key - should fail)
print("\n3️⃣ Testing Detection without API key...")
try:
    # Create minimal test audio data
    audio_data = b'\xFF\xFB' + b'\x00' * 1000  # Minimal MP3-like header + data
    audio_base64 = base64.b64encode(audio_data).decode()
    
    payload = {
        "language": "English",
        "audioFormat": "mp3", 
        "audioBase64": audio_base64
    }
    
    response = requests.post(f"{url}/api/voice-detection", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test 4: Detection endpoint (with API key - should work)
print("\n4️⃣ Testing Detection with API key...")
try:
    headers = {
        "Content-Type": "application/json",
        "x-api-key": "test-key-123"
    }
    
    response = requests.post(f"{url}/api/voice-detection", headers=headers, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
print("✅ API Testing Complete!")