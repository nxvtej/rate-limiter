# dummy backend
from fastapi import FastAPI # used for creating the FastAPI application
from fastapi.middleware.cors import CORSMiddleware # used for handling CORS
from fastapi.responses import JSONResponse # used for creating JSON responses
from fastapi import APIRouter #used for creating API routes
from fastapi import Request, Response # used for handling requests and responses
from fastapi import HTTPException # used for raising HTTP exceptions
from .routers import users, products, orders
import logging

app = FastAPI(
    title = "Test Service",
    description="This is a test service for demonstrating my rate limiter capabilities.",
    version="1.0.0",
    contact={
        "name": "Navdeep Singh",
        "email": "navdeep.s@clear.com"
    }
    
)

# CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# logging configuration and indian time format and must print the filename and line number 
logging.basicConfig(level = logging.INFO, format= '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# for creating better docs we add tags 
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])


@app.get("/health", summary="Health Check", description="Check the health of the service")
async def health_check(request: Request):
    """
    Health check endpoint to verify the service is running.
    """
    logger.info("Health check endpoint called")
    return JSONResponse(content={"status": "ok"}, status_code=200)