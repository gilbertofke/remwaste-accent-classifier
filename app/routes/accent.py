from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
# Import dependencies
from app.dependencies import get_api_key, get_redis_client
from ..models.inference import classify_audio, ENGLISH_ACCENTS
from ..utils.audio import process_url
import logging
import redis.asyncio as redis
import json

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()
logger = logging.getLogger("accent-analysis")

from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional
import re

class AnalysisRequest(BaseModel):
    url: HttpUrl = Field(description="Audio file URL")
    auth_token: Optional[str] = None
    language: str = Field(default="en", description="Language code (only 'en' supported currently)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://example.com/audio.wav",
                "auth_token": "your_auth_token_here",
                "language": "en"
            }
        }
    }

    @field_validator('url')
    @classmethod
    def validate_audio_url(cls, v):
        if not re.match(r'^https?://(?:\w+\.)+\w+/.*\.(wav|mp3|flac|ogg)$', str(v)):
            raise ValueError('Invalid audio URL format')
        return v
        
    @field_validator('language')
    @classmethod
    def validate_language(cls, v):
        if v.lower() != 'en':
            raise ValueError('Only English language analysis is currently supported')
        return v

@router.post("/analyze")
@limiter.limit("10/minute")
async def analyze_accent(
    request: AnalysisRequest,
    redis_client: redis.Redis = Depends(get_redis_client),
    api_key: str = Depends(get_api_key)
):
    try:
        # Generate cache key from URL
        cache_key = f'accent:{hash(str(request.url))}'
        cached = await redis_client.get(cache_key)
        
        if cached:
            return JSONResponse(content={"result": json.loads(cached), "source": "cache"})

        audio_data = await process_url(str(request.url))
        result = await classify_audio(audio_data, redis_client)
        if result["accent"] not in ENGLISH_ACCENTS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported accent type. Supported English accents: {ENGLISH_ACCENTS}"
            )
        
        # Enhanced response with confidence and summary
        enhanced_result = {
            "accent": result["accent"],
            "confidence": result["confidence"],
            "summary": f"This audio has {result['confidence']}% confidence of being {result['accent']} English",
            "details": result,
            "language": "en",
            "accent_types": ["British", "American", "Australian"],
            "confidence_interpretation": {
                "high": "≥80%",
                "medium": "50-79%",
                "low": "<50%"
            }
        }
        
        await redis_client.setex(cache_key, 3600, json.dumps(enhanced_result))
        return {"result": enhanced_result, "source": "fresh"}

    except HTTPException as he:
        logger.error(f"Auth error: {he.detail}")
        raise
    except Exception as e:
        logger.exception("Analysis failed")
        return JSONResponse(
            status_code=500,
            content={"error": "Analysis failed", "detail": str(e)}
        )