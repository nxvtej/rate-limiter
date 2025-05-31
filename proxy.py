from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
import httpx
import asyncio # library to write concurrent code using the async/await syntax.
import logging

from config import PRIMARY_BACKEND, REDIS_URL, MAX_CONCURRENT_REQUESTS

logging.basicConfig(level = logging.INFO, format= '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

# using for outgoing requests to primary backend 
client = httpx.AsyncClient(base_url=PRIMARY_BACKEND, follow_redirects=False,timeout=5.0)

async def forward_proxy(request: Request) -> Response:
    """
    Forward the request to the primary backend and return the response.
    """
    async with semaphore:
        try:
            url_path = request.url.path
            method = request.method
            headers = dict(request.headers) # as request.headers is immutable, we convert it to a mutable dict
            headers.pop("host", None) 
            data = await request.body()
            logger.info(f"Forwarding request to {url_path} with method {method}")
            
            if request.url.query:
                url_path += f"?{request.url.query}"
            headers["X-Forwarded-For"] = request.client.host if request.client else "unknown"
            headers["X-Forwarded-Proto"] = request.url.scheme if request.url else "http"
            
            logger.info(f"Proxying {request.method} {url_path} from {request.client.host} to {PRIMARY_BACKEND}")
            
            backend_response = await client.request(
                method=method,
                url=url_path,
                headers=headers,
                content=data
            )
            
            return Response(
                content=backend_response.content,
                status_code=backend_response.status_code,
                headers=backend_response.headers,
                media_type=backend_response.headers.get("Content-Type", "application/json")
            )
            
        except httpx.RequestError as e:
            logger.error(f"HTTPX Request Error forwarding to backend: {e}")
            raise HTTPException(status_code=503, detail="Backend service unavailable")
        except httpx.TimeoutException as e:
            logger.error(f"HTTPX Timeout Error forwarding to backend: {e}")
            raise HTTPException(status_code=504, detail="Gateway timeout")
        except Exception as e:
            logger.exception(f"Unexpected error forwarding to backend: {e}")
            raise HTTPException(status_code=500, detail="Internal Gateway error")