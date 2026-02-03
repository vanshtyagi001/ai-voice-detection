"""
AI-Generated Voice Detection API
Multi-language support: Tamil, English, Hindi, Malayalam, Telugu
"""

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Literal, Optional
import base64
import uuid
import io
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Voice Detection API",
    description="Detect AI-generated vs Human voice in multiple languages",
    version="1.0.0"
)

# Supported languages
SUPPORTED_LANGUAGES = ["Tamil", "English", "Hindi", "Malayalam", "Telugu"]

# API Key Management (In production, use environment variables and database)
VALID_API_KEYS = set(os.environ.get("API_KEYS", "test-key-123,guvi-api-key-2024").split(","))


class VoiceRequest(BaseModel):
    """Request model for voice detection"""
    language: Literal["Tamil", "English", "Hindi", "Malayalam", "Telugu"] = Field(
        ..., description="Language of the audio sample"
    )
    audioFormat: Literal["mp3"] = Field(
        default="mp3", description="Audio format (currently supports mp3)"
    )
    audioBase64: str = Field(
        ..., description="Base64 encoded MP3 audio file"
    )
    
    class Config:
        populate_by_name = True  # Accept both snake_case and camelCase

    @validator('audioBase64')
    def validate_base64(cls, v):
        """Validate base64 string"""
        if not v or len(v) < 50:
            raise ValueError("Audio data is too short or empty")
        try:
            # Add padding if needed
            padding = 4 - len(v) % 4
            if padding != 4:
                v = v + '=' * padding
            # Test decode
            base64.b64decode(v)
        except Exception:
            # Try URL-safe base64
            try:
                base64.urlsafe_b64decode(v)
            except Exception:
                raise ValueError("Invalid base64 encoding")
        return v


class SuccessResponse(BaseModel):
    """Success response model"""
    status: Literal["success"]
    language: str
    classification: Literal["AI_GENERATED", "HUMAN"]
    confidenceScore: float = Field(..., ge=0.0, le=1.0)
    explanation: str


class ErrorResponse(BaseModel):
    """Error response model"""
    status: Literal["error"]
    message: str


def verify_api_key(api_key: Optional[str]) -> bool:
    """Verify API key"""
    if not api_key:
        return False
    return api_key in VALID_API_KEYS


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An internal error occurred while processing your request"
        }
    )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "AI Voice Detection API",
        "status": "online",
        "version": "1.0.0",
        "supported_languages": SUPPORTED_LANGUAGES
    }


@app.get("/health")
async def health_check():
    """Health check for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/voice-detection", response_model=SuccessResponse)
async def detect_voice(
    request: VoiceRequest,
    x_api_key: Optional[str] = Header(None, alias="x-api-key")
):
    """
    Detect if voice sample is AI-generated or human
    
    Args:
        request: Voice detection request with audio data
        x_api_key: API key for authentication
        
    Returns:
        Classification result with confidence score
    """
    # Authenticate
    if not verify_api_key(x_api_key):
        raise HTTPException(
            status_code=401,
            detail={
                "status": "error",
                "message": "Invalid or missing API key"
            }
        )
    
    # Generate unique request ID for logging purposes
    request_id = str(uuid.uuid4())
    logger.info(f"Processing request {request_id} for language: {request.language}")
    
    try:
        # Decode audio
        try:
            audio_b64 = request.audioBase64
            # Add padding if needed
            padding = 4 - len(audio_b64) % 4
            if padding != 4:
                audio_b64 = audio_b64 + '=' * padding
            audio_data = base64.b64decode(audio_b64)
        except Exception as e:
            logger.error(f"Base64 decode error: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "Failed to decode base64 audio data"
                }
            )
        
        # Validate audio data
        if len(audio_data) < 1000:  # Too small to be valid MP3
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "Audio file is too small or corrupted"
                }
            )
        
        # Import detector (lazy import for faster startup)
        from detector import detect_ai_voice
        
        # Perform detection
        classification, confidence = detect_ai_voice(
            audio_data=audio_data,
            language=request.language.lower()  # Convert to lowercase for detector
        )
        
        # Generate explanation based on classification
        if classification == "AI_GENERATED":
            explanation = "Unnatural pitch consistency and robotic speech patterns detected"
        else:
            explanation = "Natural voice characteristics and human speech patterns detected"
        
        # Return response
        return SuccessResponse(
            status="success",
            language=request.language,
            classification=classification,
            confidenceScore=round(confidence, 2),
            explanation=explanation
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Detection error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to process audio sample"
            }
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
