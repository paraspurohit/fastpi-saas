import time
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.config.config import setting

logger = logging.getLogger("api")

RATE_LIMIT = setting.rate_limit
RATE_WINDOW = setting.rate_window

rate_limit_store = {}

CACHE_TTL = 10
response_cache = {}


async def middleware_handler(request: Request, call_next):
    start_time = time.perf_counter()
    try:
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        method = request.method
        now = time.time()
        timestamps = rate_limit_store.get(client_ip, [])
        timestamps = [t for t in timestamps if now - t < RATE_WINDOW]
        if len(timestamps) >= RATE_LIMIT:
            # raise HTTPException(status_code=429, detail="Too many requests") #fastapi.exceptions.HTTPException: 429: Too many requests
            # return HTTPException(status_code=429, detail="Too many requests")  #TypeError: 'HTTPException' object is not callable
            return JSONResponse(status_code=429, content={"detail": "Too many requests"})
        timestamps.append(now)
        rate_limit_store[client_ip] = timestamps
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        logger.info(
            f"{client_ip} | {method} {path} | "
            f"{response.status_code} | {process_time:.4f}s"
        )
        return response
    except HTTPException as exc:
        logger.warning(
            f"HTTPException | {request.method} {request.url.path} | {exc.detail}"
        )
        raise exc
    except Exception:
        logger.exception(f"Unhandled error | {request.method} {request.url.path}")
        return JSONResponse(
            status_code=500,
            content={"message": "Something went wrong"},
        )
