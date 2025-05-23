````markdown name=README.md
# REMWaste Accent Classifier

[![CI/CD](https://github.com/gilbertofke/remwaste-accent-classifier/actions/workflows/main.yml/badge.svg)](https://github.com/gilbertofke/remwaste-accent-classifier/actions)

A real-time API for English accent classification from audio URLs, powered by Hugging Face models, Redis caching, and Prometheus monitoring.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [API Usage](#api-usage)
- [Environment Variables](#environment-variables)
- [Testing](#testing)
- [License](#license)

## Features

- **Real-time accent analysis** via a FastAPI endpoint.
- **URL-based audio ingestion** (supports HTTP/HTTPS links to audio files).
- **Accent types detected:** British, American, Australian.
- **Hugging Face model integration** for audio classification.
- **Redis caching** for performance and efficiency.
- **API key authentication** for secure access.
- **Rate limiting** to prevent abuse.
- **Prometheus metrics** for monitoring.
- **Docker support** for easy deployment.

## Quick Start

### Prerequisites

- Python 3.10+
- [Docker](https://www.docker.com/) (optional)
- Redis (Upstash or other, see `.env.example`)

### Local Installation

```bash
git clone https://github.com/gilbertofke/remwaste-accent-classifier.git
cd remwaste-accent-classifier
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
# Fill in the required environment variables in .env
uvicorn app.main:app --reload
```

### Docker

```bash
docker build -t accent-classifier .
docker run --env-file .env -p 8000:8000 accent-classifier
```

## API Usage

### Analyze Accent

**Endpoint:** `POST /api/v1/analyze`

**Headers:**
- `X-API-Key`: Your API key

**Request Body (JSON):**
```json
{
  "url": "https://example.com/audio.wav",
  "language": "en"
}
```

**Response Example:**
```json
{
  "result": {
    "accent": "British",
    "confidence": 92.3,
    "summary": "This audio has 92.3% confidence of being British English",
    "language": "en",
    "accent_types": ["British", "American", "Australian"],
    "confidence_interpretation": {
      "high": "≥80%",
      "medium": "50-79%",
      "low": "<50%"
    }
  },
  "source": "fresh"
}
```

**Notes:**
- Only English accents are supported.
- Audio URL must be HTTP/HTTPS and point to `.wav`, `.mp3`, `.flac`, or `.ogg` files.
- Cached results are served when available.

## Environment Variables

Copy `.env.example` and fill in your credentials:

- `HF_TOKEN`: Hugging Face API token (required)
- `HF_MODEL_ID`: Hugging Face model ID (default: `speechbrain/lang-id-voxlingua107-ecapa`)
- `API_KEY`: API key for authentication
- `UPSTASH_REDIS_URL`: Redis connection URL (Upstash format)
- `UPSTASH_REDIS_TOKEN`: Redis authentication token
- `RATE_LIMIT_PER_MINUTE`: Requests per minute per API key (default: 10)

## Testing

Run tests with:

```bash
pytest
```

## Monitoring

Prometheus metrics are available at `/metrics` when running the server.

## License

MIT License. See [LICENSE](LICENSE).

---

*Developed by [gilbertofke](https://github.com/gilbertofke). Contributions welcome!*
````