REDIS_URL = "redis://localhost:6379/0"
PRIMARY_BACKEND = "http://127.0.0.1:8001/"
MAX_CONCURRENT_REQUESTS = 5
RATE_LIMITS = {
    "GET": 5,  
    "POST": 5,  
    "PUT": 5,   
    "DELETE": 5 
}

TIME_WINDOW = 60  
# docker run -d --name redis-container -p 6379:6379 -v redis-data:/data redis
