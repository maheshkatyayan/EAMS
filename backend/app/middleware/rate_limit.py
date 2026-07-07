import time
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.config import settings

try:
    import redis
    _r = redis.from_url(settings.REDIS_URL, socket_connect_timeout=1)
except Exception:
    _r = None


async def rate_limit(request: Request, call_next):
    if request.url.path.startswith("/api") and _r is not None:
        key = f"rl:{request.client.host if request.client else 'x'}:{int(time.time() // 60)}"
        try:
            n = _r.incr(key)
            if n == 1:
                _r.expire(key, 60)
            if n > settings.RATE_LIMIT_PER_MINUTE:
                return JSONResponse({"detail": "Too many requests"}, status_code=429)
        except Exception:
            pass  # fail open if redis is unreachable
    return await call_next(request)
