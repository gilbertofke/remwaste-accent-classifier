# REMWaste Accent Classifier

[![CI/CD](https://github.com/gilbertofke/remwaste-accent-classifier/actions/workflows/main.yml/badge.svg)](https://github.com/gilbertofke/remwaste-accent-classifier/actions)

A real-time API for classifying English accents from audio URLs. Powered by Hugging Face models, Redis caching, and Prometheus monitoring.


## 📚 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [API Usage](#api-usage)
- [Environment Variables](#environment-variables)
- [Testing](#testing)
- [Monitoring](#monitoring)
- [License](#license)



## 🚀 Features

- ⚡ **Real-time accent classification** via FastAPI.
- 🌐 **URL-based audio ingestion** (`.wav`, `.mp3`, `.flac`, `.ogg`).
- 🗣️ **Accents supported:** British, American, Australian.
- 🤗 **Hugging Face model integration**.
- 🧠 **Redis caching** for improved response times.
- 🔐 **API key authentication**.
- 🚫 **Rate limiting** to prevent abuse.
- 📈 **Prometheus metrics** for monitoring.
- 🐳 **Docker support** for easy deployment.

---

## ⚡ Quick Start

### Prerequisites

- Python 3.10+
- [Docker](https://www.docker.com/) (optional)
- Redis instance (e.g., [Upstash](https://upstash.com))

### Local Setup
git clone https://github.com/gilbertofke/remwaste-accent-classifier.git
cd remwaste-accent-classifier
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env  # Update .env with your credentials
uvicorn app.main:app --reload
Docker Setup
bash

docker build -t accent-classifier .
docker run --env-file .env -p 8000:8000 accent-classifier
🧪 API Usage
POST /api/v1/analyze
Headers:

X-API-Key: Your API key

Request Body:
{
  "url": "https://example.com/audio.wav",
  "language": "en"
}
Example Response:

json
Copy
Edit
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
Notes:

Only English accents are supported.

Audio URLs must use HTTP/HTTPS and point to .wav, .mp3, .flac, or .ogg files.

Cached results are served when available.

🔧 Environment Variables
Copy .env.example and provide the required values:

Variable	Description
HF_TOKEN	Hugging Face API token (required)
HF_MODEL_ID	Hugging Face model ID (speechbrain/lang-id-voxlingua107-ecapa by default)
API_KEY	API key to secure endpoint access
UPSTASH_REDIS_URL	Redis connection URL (Upstash or other)
UPSTASH_REDIS_TOKEN	Redis authentication token
RATE_LIMIT_PER_MINUTE	Request limit per minute per API key (default: 10)

🧪 Testing
Run the test suite using:

pytest
📊 Monitoring
Prometheus-compatible metrics are exposed at:


/metrics
📄 License
This project is licensed under the MIT License.

🛠 Built with passion by gilbertofke
🤝 Contributions are welcome!