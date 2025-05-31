# Rate Limiting and Traffic Shaping Gateway

## Project Overview

This project is a high-performance API Gateway built with FastAPI designed to protect and manage traffic to backend services. It demonstrates critical backend engineering concepts including distributed rate limiting, traffic shaping (concurrency control), and transparent request proxying.

It serves as a robust front-door for microservices, preventing overload, ensuring fair resource allocation, and centralizing common concerns like traffic management.

## Key Features

- **Distributed Rate Limiting**: Implements a fixed-window counter algorithm using Redis to enforce rate limits per client IP across multiple gateway instances, returning 429 Too Many Requests when limits are exceeded.
- **Transparent Request Proxying**: Forwards all valid incoming HTTP requests to a configurable upstream backend service using httpx, preserving methods, headers, and body.
- **Traffic Shaping (Concurrency Control)**: Limits the total number of simultaneous requests forwarded to the backend using `asyncio.Semaphore`, preventing backend overload during traffic spikes.
- **Monitoring & Health Checks**: Provides basic in-memory metrics (total processed/blocked requests) and a `/health` endpoint to check the gateway's status and connectivity to Redis and the backend.
- **Configurable**: All critical parameters are easily set via environment variables.

## Architectural Diagram

```
+------------------+      +--------------------------------------------------+      +---------------------+
|     Client       | ---> |  Rate Limiting & Traffic Shaping Gateway (FastAPI) | --> | Upstream Backend     |
|   (User/App)     |      +--------------------------------------------------+      |     Service(s)       |
+------------------+                                                       ^        +---------------------+
        |                                                                  |              ^
        v                                                                  |              |
+------------------------------+                                          |              |
| 1. Incoming Request          |                                          |              |
+------------------------------+                                          |              |
| 2. Client Identification     |                                          |              |
+------------------------------+                                          |              |
| 3. Distributed Rate Limiting |                                          |              |
|    (Checks/Updates Redis)    |                                          |              |
+------------------------------+                                          |              |
| 4. Concurrency Control       |                                          |              |
|    (Semaphore)               |                                          |              |
+------------------------------+                                          |              |
| 5. Request Proxying          |                                          |              |
+------------------------------+                                          |              |
| 6. Backend Response Handling | <----------------------------------------+              |
+------------------------------+                                                         |
        |                                                                              v
        +-----------------------------------------------------------------------+
        | 7. Metrics & Logging (Internal counters, `/health` endpoint)         |
        +-----------------------------------------------------------------------+
```

## Architectural Components Explained

- **Client**: Users or applications making requests.
- **Gateway (FastAPI)**: Intercepts requests, applies rate limiting and concurrency, then proxies to the backend. It's the central control point.
- **Redis**: An external, in-memory data store used by the Gateway for shared, distributed rate limiting counters.
- **Upstream Backend Service(s)**: The actual application services (simulated by `backend_app`) that process business logic.
- **Metrics & Logging**: Internal tracking of gateway operations and a `/health` endpoint for external monitoring.

## Technologies Used

- Python 3.9+
- FastAPI & Uvicorn
- Redis (redis-py client)
- httpx

## Getting Started

### Prerequisites

- Python 3.9+ and pip
- Redis Server (Docker Desktop recommended)

### Setup Instructions

**Clone the Repository:**

```bash
git clone [your-repository-url]
cd rate_limiter_gateway
```

**Set up Virtual Environment & Install Dependencies:**

```bash
python -m venv venv
.env\Scripts\Activate.ps1  # Windows PowerShell
# or
source venv/bin/activate     # Linux/macOS

pip install -r requirements.txt
```

**Start Redis Server:**

```bash
docker run --name my-redis -p 6379:6379 -d redis
```

**Configure Environment Variables:**
Create a `.env` file (see `config.py` for defaults).

**Run Dummy Backend:**

```bash
uvicorn backend_app.main:app --port 8001 --reload
```

**Run Gateway:**

```bash
uvicorn main:app --port 8000 --reload
```

## How to Test

Ensure both the dummy backend (port 8001) and the Gateway (port 8000) are running.

**Health Check:**

```bash
curl http://127.0.0.1:8000/health
```

_Expected: status: OK, Redis & backend Connected._

**Proxying Test:**

```bash
curl http://127.0.0.1:8000/users/1
```

_Expected: A response from the dummy backend's user endpoint._

**Rate Limiting Test:**

```bash
for i in $(seq 1 10); do curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/; done
```

_Expected: Initial 200 OK responses, then 429 Too Many Requests after exceeding the limit._

## Future Enhancements

- Advanced Rate Limiting Algorithms (Token Bucket, Leaky Bucket)
- Dynamic Rule Management via API
- API Key Based Rate Limiting
- Prometheus/Grafana Integration
- Circuit Breaker Pattern
- Caching Layer
- TLS/SSL Termination
