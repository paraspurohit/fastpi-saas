import time
import logging
import redis
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from app.config.config import setting

logger = logging.getLogger("api")

redis_client = redis.Redis(
    host=setting.redis_host,
    port=setting.redis_port,
    decode_responses=True
)


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        try:
            client_ip = get_client_ip(request)
            now = time.time_ns()
            key = f"rate:{client_ip}"

            pipe = redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, now - setting.rate_window)
            pipe.zadd(key, {now: now})
            pipe.zcard(key)
            pipe.expire(key, setting.rate_window)

            _, _, request_count, _ = pipe.execute()

            if request_count > setting.rate_limit:
                raise HTTPException(status_code=429, detail="Too many requests")

            response = await call_next(request)

            process_time = time.perf_counter() - start_time
            response.headers["X-Process-Time"] = f"{process_time:.4f}s"

            logger.info(
                "request_log",
                extra={
                    "client_ip": client_ip,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time": round(process_time, 4),
                },
            )

            return response

        except HTTPException as exc:
            logger.warning(
                "rate_limit_triggered",
                extra={
                    "path": request.url.path,
                    "detail": exc.detail,
                },
            )
            raise exc

        except Exception:
            logger.exception("unexpected_error")
            return JSONResponse(
                status_code=500,
                content={"message": "Internal Server Error"},
            )
