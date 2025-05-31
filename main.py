from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
import logging
import httpx

from config import (
    PRIMARY_BACKEND,
    REDIS_URL,
    MAX_CONCURRENT_REQUESTS,
    RATE_LIMITS,
    TIME_WINDOW,
)

from proxy import forward_proxy

app = FastAPI(
    title="Rate Limiter",
    description="A simple rate limiter service",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level = logging.INFO, format= '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

redis_client:redis.Redis = None
total_requests_processed = 0
total_requests_blocked = 0

@app.on_event("startup")
async def start():
    global redis_client
    try:
        redis_client = redis.from_url(REDIS_URL)
        await redis_client.ping()
        logger.info("Successfully Connected to Redis at %s", REDIS_URL)
    except redis.ConnectionError as e:
        logger.critical("Failed to connect to Redis at %s: %s", REDIS_URL, e)
        raise HTTPException(status_code=500, detail="Redis connection failed")
    
    logger.info(f"Gateway started with primary backend: {PRIMARY_BACKEND}")
    logger.info(f"Configured Rate Limits: {RATE_LIMITS} requests per {TIME_WINDOW} seconds")
    logger.info(f"Max Concurrent Requests: {MAX_CONCURRENT_REQUESTS}")
    
@app.on_event("shutdown")
async def shutdown():
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")
        
async def is_rate_limited(client_ip: str)->bool:
    """
    Check if the client IP is rate limited based on the configured limits.
    """
    global total_requests_processed, total_requests_blocked
    total_requests_processed += 1

    logger.info(f"Processing request from {client_ip}. (Rate limiting logic is pending full implementation in Phase 2.)")
    return False


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def catch_all_proxy(request: Request, path: str) -> Response:
    client_ip = request.client.host

    if await is_rate_limited(client_ip):
        raise HTTPException(
            status_code=429,
            detail=f"Too Many Requests. Limit: {RATE_LIMITS[request.method]} per {TIME_WINDOW}s. Please retry after {TIME_WINDOW} seconds."
        )
    return await forward_proxy(request)


# --- Health Check Endpoint ---
@app.get("/health", summary="Gateway Health Check")
async def health_check():
    """
    Provides health status of the gateway, including connectivity to Redis and the backend.
    Also exposes basic in-memory metrics.
    """
    redis_status = "Disconnected"
    try:
        if redis_client:
            await redis_client.ping()
            redis_status = "Connected"
        else:
            redis_status = "Not Initialized"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        redis_status = f"Disconnected: {e}"

    backend_status = "Unknown"
    try:
        async with httpx.AsyncClient() as client:
            backend_response = await client.get(f"{PRIMARY_BACKEND}/health", timeout=2.0)
            backend_response.raise_for_status() # Raises HTTPStatusError for 4xx/5xx responses
            backend_status = "Connected"
    except httpx.RequestError as e:
        logger.error(f"Backend health check failed (connection error): {e}")
        backend_status = f"Disconnected (connection error): {e}"
    except httpx.HTTPStatusError as e:
        logger.warning(f"Backend health check failed (HTTP status error): {e.response.status_code}")
        backend_status = f"Connected (backend error status: {e.response.status_code})" # Backend responded, but with error status
    except Exception as e:
        logger.exception(f"Unexpected error during backend health check: {e}")
        backend_status = f"Error: {e}"

    overall_status = "OK"
    if "Disconnected" in redis_status or "Disconnected" in backend_status or "Error" in backend_status:
        overall_status = "DEGRADED" if ("Connected" in redis_status or "Connected" in backend_status) else "UNHEALTHY"

    return {
        "status": overall_status,
        "redis_status": redis_status,
        "backend_status": backend_status,
        "metrics": {
            "total_requests_processed": total_requests_processed,
            "total_requests_blocked": total_requests_blocked
        }
    }
