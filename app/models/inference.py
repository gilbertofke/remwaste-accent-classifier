import os
import logging
import redis.asyncio as redis
from huggingface_hub import AsyncInferenceClient
from tenacity import retry, stop_after_attempt, wait_exponential
import hashlib

logger = logging.getLogger("model-inference")

ENGLISH_ACCENTS = ["British", "American", "Australian"]

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
async def classify_audio(audio: bytes, redis_client: redis.Redis) -> dict:
    """Classify audio using Hugging Face model with Redis caching"""
    try:
        # Generate cache key from audio hash
        audio_hash = hashlib.sha256(audio).hexdigest()
        cache_key = f'model:{audio_hash}'
        
        # Check cache
        cached = await redis_client.get(cache_key)
        if cached:
            return {"status": "success", "data": cached, "cached": True}

        # Initialize HF client
        client = AsyncInferenceClient(token=os.getenv("HF_TOKEN"))
        
        # Perform inference
        # Note: We're sending raw audio bytes to the inference API
        result = await client.audio_classification(
            audio,
            model=os.getenv("HF_MODEL_ID", "speechbrain/lang-id-voxlingua107-ecapa")
        )
        
        # Cache result for 1 hour
        await redis_client.setex(cache_key, 3600, result)
        
        return {"status": "success", "data": result, "cached": False}

    except Exception as e:
        logger.error(f"Inference failed: {str(e)}")
        return {"status": "error", "message": "Model inference failed"}