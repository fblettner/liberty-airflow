import asyncio
import logging
import sys

# Configure global logging
logging.basicConfig(
    level=logging.WARN,  
    format="%(asctime)s - %(levelname)s - %(message)s",  
)

import os
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.utils.jwt import JWT
from app.controllers.api_controller import ApiController
from app.routes.api_routes import setup_api_routes
from app.airflow.manager.start import start_airflow
from app.airflow.manager.stop import stop_airflow

import uvicorn

class BackendAPI:
    def __init__(self):
        self.jwt = JWT()
        self.api_controller = ApiController(self.jwt)

    def setup_routes(self, app: FastAPI):
        setup_api_routes(app, self.api_controller, self.jwt)


description = """
**Liberty API** provides a powerful and scalable backend for managing authentication, 
database operations, and framework functionalities in the **Liberty Framework**. 

### 🔹 Key Features:
- **Authentication & Authorization**: Secure endpoints with JWT tokens and OAuth2.
- **Database Management**: Query, insert, update, and delete records across multiple pools.
- **Framework Controls**: Manage modules, applications, themes, and logs.
- **Security & Encryption**: Encrypt data and ensure safe database access.
- **Logging & Auditing**: Retrieve and analyze logs for security and debugging.

### 🔹 Authentication
- **`/api/auth/token`** - Generate a JWT token for authentication.
- **`/api/auth/user`** - Retrieve authenticated user details.


**🔗 Explore the API using Swagger UI (`/api/test`) or Redoc (`/api`).**
"""

# Create the FastAPI app
app = FastAPI(
    title="Liberty Airflow",
    description=description,
    version="1.0.0",
    docs_url="/api/test",  # Swagger UI
    redoc_url="/api",  # ReDoc
    openapi_url="/liberty-api.json",  # OpenAPI schema
)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom handler for HTTPExceptions to include additional fields.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "failed",
            "message": exc.detail or "An unexpected error occurred"
        },
    )

# Initialize BackendAPI and register routes and sockets
backend_api = BackendAPI()
backend_api.setup_routes(app)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    print("Shutting down...")
    stop_airflow()
    await asyncio.sleep(0) 


def main():
    """Entry point for running the application."""
    start_airflow()
    
    config = uvicorn.Config("app.main:app", host="0.0.0.0", port=8082, reload=True, log_level="warning")
    server = uvicorn.Server(config)

    try:
        logging.warning("Starting Liberty Airflow... Press Ctrl+C to stop.")
        logging.warning("Liberty Airflow started at: http://0.0.0.0:8082")
        server.run()
    except KeyboardInterrupt:
        logging.warning("Server shutting down gracefully...")
        sys.exit(0)  # Exit without error

if __name__ == "__main__":
    main()

# Set the lifespan handler
app.router.lifespan_context = lifespan