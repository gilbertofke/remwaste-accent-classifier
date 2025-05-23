import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import Mock, patch, AsyncMock
import redis

@pytest.fixture
def mock_redis():
    return Mock(spec=redis.Redis)

@pytest.fixture
def client():
    return TestClient(app)

@patch('app.models.inference.AsyncInferenceClient')
async def test_full_pipeline_success(mock_client, client, mock_redis):
    # Mock responses
    mock_redis.get = Mock(side_effect=[None, 'cached_result'])
    mock_redis.setex = Mock()
    mock_client.return_value.text_to_speech = AsyncMock(return_value='result')

    # First request (cache miss)
    response = client.post(
        "/analyze",
        json={"url": "https://example.com/audio.wav"},
        headers={"X-API-Key": "baca9cd9afbfd7668ddae6cb9f964ab0cbc9a74f5351a31f526d05bbb858c67b"}
    )
    assert response.status_code == 200
    assert not response.json()['cached']

    # Second request (cache hit)
    response = client.post(
        "/analyze",
        json={"url": "https://example.com/audio.wav"},
        headers={"X-API-Key": "baca9cd9afbfd7668ddae6cb9f964ab0cbc9a74f5351a31f526d05bbb858c67b"}
    )
    assert response.status_code == 200
    assert response.json()['cached']

async def test_invalid_url_format(client):
    response = client.post(
        "/analyze",
        json={"url": "invalid_url"},
        headers={"X-API-Key": "baca9cd9afbfd7668ddae6cb9f964ab0cbc9a74f5351a31f526d05bbb858c67b"}
    )
    assert response.status_code == 422
    assert "Invalid audio URL format" in response.text

@patch('app.models.inference.classify_audio')
async def test_retry_logic(mock_classify, client):
    mock_classify.side_effect = Exception("Timeout")
    response = client.post(
        "/analyze",
        json={"url": "https://example.com/audio.wav"},
        headers={"X-API-Key": "baca9cd9afbfd7668ddae6cb9f964ab0cbc9a74f5351a31f526d05bbb858c67b"}
    )
    assert mock_classify.call_count == 3
    assert response.status_code == 500