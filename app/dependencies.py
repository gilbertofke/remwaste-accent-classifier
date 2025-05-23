from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    HF_TOKEN: str = Field(
        default="",
        description="HuggingFace API token",
        min_length=40,  # HF tokens are typically longer
        alias="HF_TOKEN"
    )
    
    @field_validator('HF_TOKEN')
    @classmethod
    def validate_hf_token(cls, v):
        if not v:
            raise ValueError('HuggingFace API token is required')
        return v
    API_KEY: str = Field(
        default="",
        min_length=32,
        description="API key for authentication",
        alias="API_KEY"
    )
    
    @field_validator('API_KEY')
    @classmethod
    def validate_api_key(cls, v):
        if not v:
            raise ValueError('API key is required for authentication')
        if len(v) < 32:
            raise ValueError('API key must be at least 32 characters long')
        return v
    UPSTASH_REDIS_URL: str = Field(
        default="",
        description="Redis connection URL",
        pattern=r'^https?://.*.upstash.io$',
        alias="UPSTASH_REDIS_URL"
    )
    
    @field_validator('UPSTASH_REDIS_URL')
    @classmethod
    def validate_redis_url(cls, v):
        if not v:
            raise ValueError('Redis connection URL is required')
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Redis URL must start with http:// or https://')
        if not v.endswith('.upstash.io'):
            raise ValueError('Only Upstash Redis URLs are supported')
        return v
    UPSTASH_REDIS_TOKEN: str = Field(
        default="",
        description="Redis authentication token",
        min_length=20,
        alias="UPSTASH_REDIS_TOKEN"
    )
    
    @field_validator('UPSTASH_REDIS_TOKEN')
    @classmethod
    def validate_redis_token(cls, v):
        if not v:
            raise ValueError('Redis authentication token is required')
        if len(v) < 20:
            raise ValueError('Redis token must be at least 20 characters long')
        return v
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Rate limit per minute",
        alias="RATE_LIMIT_PER_MINUTE"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        populate_by_name=True  # Crucial for alias mapping
    )


# Add these imports at the top
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
import redis.asyncio as redis
from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_exponential


@lru_cache()
def get_settings() -> Settings:
    return Settings()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
async def get_redis_client() -> redis.Redis:
    """Create Redis connection pool with retry logic and authentication"""
    settings = get_settings()
    client = redis.from_url(
        settings.UPSTASH_REDIS_URL,
        username="default",
        password=settings.UPSTASH_REDIS_TOKEN,
        decode_responses=True,
        ssl=True,
        socket_timeout=5,
        retry_on_timeout=True
    )
    if not isinstance(client, redis.Redis):
        raise RuntimeError("Failed to create Redis client")
    return client

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key: str = Security(api_key_header)) -> str:
    settings = get_settings()
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API Key is required"
        )
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )
    return api_key