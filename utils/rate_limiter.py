from functools import wraps
from collections import defaultdict
from datetime import datetime, timedelta
from flask import request, jsonify

_request_log: dict = defaultdict(list)


def rate_limit(max_requests: int = 30, window_seconds: int = 60):
    """Simple in-memory rate limiter — no extra dependencies required."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            ip = request.remote_addr or "unknown"
            now = datetime.utcnow()
            cutoff = now - timedelta(seconds=window_seconds)

            _request_log[ip] = [t for t in _request_log[ip] if t > cutoff]

            if len(_request_log[ip]) >= max_requests:
                return jsonify({"error": "Too many requests. Please wait and try again."}), 429

            _request_log[ip].append(now)
            return f(*args, **kwargs)
        return wrapped
    return decorator
