import time
from collections import Counter
from typing import Dict, Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class Metrics:
    """Tiny in-memory metrics.

    Not Prometheus format; intended for lightweight monitoring and debugging.
    """

    def __init__(self) -> None:
        self.started_at = time.monotonic()
        self.total_requests = 0
        self.requests_by_path = Counter()
        self.requests_by_status = Counter()

    def snapshot(self) -> Dict[str, Any]:
        now = time.monotonic()
        return {
            "uptime_seconds": int(now - self.started_at),
            "total_requests": int(self.total_requests),
            "requests_by_path": dict(self.requests_by_path),
            "requests_by_status": dict(self.requests_by_status),
        }


class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, metrics: Metrics):
        super().__init__(app)
        self.metrics = metrics

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        try:
            path = request.url.path
            self.metrics.total_requests += 1
            self.metrics.requests_by_path[path] += 1
            self.metrics.requests_by_status[str(response.status_code)] += 1
        except Exception:
            # Never break the API because of metrics.
            pass
        return response
