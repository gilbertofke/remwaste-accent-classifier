from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator
import time

ACCENT_REQUESTS = Counter(
    'accent_requests_total',
    'Total number of analysis requests',
    ['method', 'endpoint', 'http_status']
)

ACCENT_PROCESS_TIME = Histogram(
    'accent_process_seconds',
    'Time spent processing accent analysis',
    ['method', 'endpoint']
)

def setup_prometheus(app):
    Instrumentator().instrument(app).expose(app)

async def monitor_request(request, call_next):
    start_time = time.time()
    method = request.method
    endpoint = request.url.path
    
    try:
        response = await call_next(request)
        ACCENT_REQUESTS.labels(method, endpoint, response.status_code).inc()
        return response
    finally:
        duration = time.time() - start_time
        ACCENT_PROCESS_TIME.labels(method, endpoint).observe(duration)