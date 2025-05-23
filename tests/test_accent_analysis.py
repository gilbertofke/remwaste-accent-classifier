import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import AsyncMock, patch

@pytest.fixture
def client():
    return TestClient(app)

def test_successful_analysis(client):
    with patch('app.routes.accent.process_url') as mock_process, \
         patch('app.routes.accent.classify_audio') as mock_classify:
        
        mock_process.return_value = b'audio_data'
        mock_classify.return_value = {"status": "success", "data": "result"}
        
        response = client.post("/api/v1/analyze", 
            json={"url": "https://valid.audio/file.mp3"},
            headers={"X-API-Key": "valid_key"}
        )
        
        assert response.status_code == 200
        assert response.json()["source"] == "fresh"

def test_cached_response(client):
    with patch('app.routes.accent.redis.get') as mock_redis:
        mock_redis.return_value = 'cached_result'
        response = client.post("/api/v1/analyze", 
            json={"url": "https://cached.audio/file.mp3"},
            headers={"X-API-Key": "valid_key"}
        )
        
        assert response.status_code == 200
        assert response.json()["source"] == "cache"

def test_invalid_url_handling(client):
    response = client.post("/api/v1/analyze", 
        json={"url": "ftp://invalid.protocol/file"},
        headers={"X-API-Key": "valid_key"}
    )
    assert response.status_code == 400
    assert "Invalid URL scheme" in response.json()["detail"]

def test_authentication_failure(client):
    response = client.post("/api/v1/analyze", 
        json={"url": "https://valid.audio/file.mp3"},
        headers={"X-API-Key": "invalid_key"}
    )
    assert response.status_code == 401
    assert "Invalid API Key" in response.json()["detail"]