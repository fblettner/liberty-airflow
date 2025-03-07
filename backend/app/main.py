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
from fastapi_socketio import SocketManager
from contextlib import asynccontextmanager
from app.utils.jwt import JWT
from app.controllers.api_controller import ApiController
from app.routes.api_routes import setup_api_routes
from app.airflow.manager.start import start_airflow
from app.airflow.manager.stop import stop_airflow
from app.utils.common import load_env
from app.public import get_frontend_assets_path, get_offline_assets_path
from app.routes.react_routes import setup_react_routes
from app.controllers.socket_controller import SocketController
from app.routes.socket_routes import setup_socket_routes
from app.controllers.setup_controller import SetupController
from app.routes.setup_routes import setup_setup_routes
import uvicorn

class BackendAPI:
    def __init__(self):
        self.jwt = JWT()
        self.socket_controller = SocketController()
        self.api_controller = ApiController(self.jwt)
        self.setup_controller = SetupController(self.api_controller, self.jwt)
        self.socket_manager = None

    def setup_routes(self, app: FastAPI):
        setup_api_routes(app, self.api_controller, self.jwt)
        setup_react_routes(app)
        setup_socket_routes(app, self.socket_controller)
        setup_setup_routes(app, self.setup_controller)

    def setup_sockets(self, app: FastAPI):
        # Attach Socket.IO manager

        self.socket_manager = SocketManager(app, cors_allowed_origins="*")
        # Pass the AsyncServer instance to the SocketController
        self.socket_controller.socketio_mount(app)
        self.socket_controller.set_api_controller(self.api_controller)
        

        @self.socket_controller.io.on("connect")
        async def connect(sid, environ, auth):
            client = environ.get("asgi.scope", {}).get("client", ("unknown", "unknown"))
            self.socket_controller.connected_clients[sid] = {"user": auth.get("user"), "app": auth.get("app"), "client": client}

            """Handle new socket connections."""
            app_room = f"appsID_{auth["app"]}"  # Extract app from the handshake
            await self.socket_controller.io.enter_room(sid, app_room, namespace="/")
            logging.debug(f"Socket connected: {sid}, joined room: {app_room}")


        @self.socket_controller.io.on("reserve")
        async def reserve(sid, record_id):
            """
            Handle reserve event for a specific record ID.
            Goal: Check if a record ID is reserved (already in a room).
            - If it's reserved, send KO.
            - If not reserved, mark it as reserved and send OK.
            """
            # Access rooms in the default namespace "/"
            rooms = self.socket_controller.io.manager.rooms.get("/", {})

            # Check if the record_id exists as a key in the rooms
            if record_id in rooms:
                # Record is already reserved
                room_participants = rooms[record_id]
                is_current_socket_in_room = sid in room_participants

                if is_current_socket_in_room:
                    logging.debug(f"Record reserved by the current user: {record_id}")
                    return {"status": "OK", "record": record_id}
                else:
                    logging.debug(f"Record reserved: {record_id}")
                    return {"status": "KO", "record": record_id}
            else:
                # Record is not reserved, reserve it by adding the socket to the room
                logging.debug(f"Socket {sid} reserve record: {record_id}")
                await self.socket_controller.io.enter_room(sid, record_id)
                return {"status": "OK", "record": record_id}

        @self.socket_controller.io.on("release")
        async def release(sid, record_id):
            """Handle release event for a specific record ID."""
            await self.socket_controller.io.leave_room(sid, record_id, namespace="/")
            logging.debug(f"Socket {sid} release record: {record_id}")


        @self.socket_controller.io.on("signout")
        async def signout(sid):
            """Handle user signout and clean up their rooms."""
            for room in self.socket_controller.io.rooms(sid):
                if room.startswith("appsID_"):
                    await self.socket_controller.io.leave_room(sid, room, namespace="/")
                    self.socket_controller.connected_clients.pop(sid, None)  
                    logging.debug(f"Socket {sid} left app room: {room}")

        @self.socket_controller.io.on("disconnect")
        async def disconnect(sid, reason):
            """Handle socket disconnection."""
            for room in self.socket_controller.io.rooms(sid):
                await self.socket_controller.io.leave_room(sid, room, namespace="/")
                self.socket_controller.connected_clients.pop(sid, None)  
                logging.debug(f"Socket {sid} left room: {room}")

            logging.debug(f"Socket disconnected: {sid}")

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
backend_api.setup_sockets(app)

@asynccontextmanager
async def lifespan(app: FastAPI):
    api_instance = backend_api.api_controller.api
    app.mount(
        "/offline/assets",
        StaticFiles(directory=get_offline_assets_path(), html=True),
        name="assets",
    )

    try: 
        app.mount(
            "/assets",
            StaticFiles(directory=get_frontend_assets_path(), html=True),
            name="assets",
        )     

        liberty_config = api_instance.load_liberty_properties()
        await api_instance.default_pool(liberty_config)
        airflow_config = api_instance.load_airflow_properties()
        await api_instance.airflow_pool(airflow_config)

        app.state.offline_mode = False
    except Exception as e:
        logging.error(f"Error mounting assets: {e}")
        app.state.offline_mode = True      
    yield
    print("Shutting down...")
    stop_airflow()
    await asyncio.sleep(0) 


def main():
    """Entry point for running the application."""

    load_env() 
    start_airflow()
    fastapi_host = os.getenv("FASTAPI_HOST", "localhost")  
    fastapi_port = os.getenv("FASTAPI_PORT", 8082)
    
    config = uvicorn.Config("app.main:app", host=fastapi_host, port=fastapi_port, reload=True, log_level="warning")
    server = uvicorn.Server(config)

    try:
        print("Starting Liberty Airflow... Press Ctrl+C to stop.")
        print(f"Liberty Airflow started at: http://{fastapi_host}:{fastapi_port}")
        server.run()
    except KeyboardInterrupt:
        logging.warning("Server shutting down gracefully...")
        sys.exit(0)  # Exit without error

if __name__ == "__main__":
    main()

# Set the lifespan handler
app.router.lifespan_context = lifespan