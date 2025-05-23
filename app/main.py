from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import accent
from .dependencies import get_redis_client
import os

app = FastAPI(title="Accent Analysis API", version="0.1.0")

# Initialize Prometheus monitoring
from .monitoring.prometheus import setup_prometheus
setup_prometheus(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Redis connection
@app.on_event("startup")
async def startup_event():
    app.state.redis = await get_redis_client()

app.include_router(accent.router, prefix="/api/v1", tags=["accent"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "redis_connected": bool(app.state.redis)}