"""Quick test of the detector directly"""
import sys
sys.path.insert(0, 'd:/CS/Guvi Hackathon')

import numpy as np
import soundfile as sf
import tempfile
import base64
import logging

# Enable verbose logging
logging.basicConfig(level=logging.DEBUG)

# Create test audio - human-like voice
sr = 16000
duration = 3
t = np.linspace(0, duration, sr * duration)
f0 = 150
voice = sum((0.5 / i) * np.sin(2 * np.pi * f0 * i * t) for i in range(1, 8))
voice += np.random.randn(len(voice)) * 0.02
voice = voice / np.max(np.abs(voice)) * 0.8

# Save as MP3
with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
    sf.write(f.name, voice, sr, format='MP3')
    with open(f.name, 'rb') as mp3f:
        mp3_bytes = mp3f.read()

print(f'Created MP3: {len(mp3_bytes)} bytes')
print(f'First 20 bytes (hex): {mp3_bytes[:20].hex()}')

# Test detector directly
from detector import detect_ai_voice

result, confidence = detect_ai_voice(mp3_bytes, 'english')
print(f'\nResult: {result}')
print(f'Confidence: {confidence}')
