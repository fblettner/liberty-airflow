import os
import logging
import sys
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Import the original FastAPI app and controllers
from liberty.main import BackendAPI
from liberty.services.rest_services import Rest
from liberty.routes.api_routes import setup_api_routes
from liberty.routes.socket_routes import setup_socket_routes
from liberty.routes.setup_routes import setup_setup_routes
from liberty.controllers.api_controller import ApiController
from liberty.scheduler.controllers.airflow_controller import AirflowController
from liberty.scheduler.routes.airflow_routes import setup_airflow_routes
from liberty.scheduler.utils.jwt import CustomJWT
from liberty.scheduler.services.api_services import CustomAPI
from liberty.scheduler.routes.react_routes import setup_react_routes
from liberty.scheduler.public import get_frontend_assets_path, get_offline_assets_path
from liberty.scheduler.airflow.manager.stop import stop_airflow
from liberty.scheduler.airflow.manager.start import start_airflow
  

# Initialize logging
logging.basicConfig(level=logging.WARN, format="%(asctime)s - %(levelname)s - %(message)s")

# Extend the BackendAPI for Custom Logic
class CustomBackendAPI(BackendAPI):
    def __init__(self):
        super().__init__()  
        self.jwt = CustomJWT()
        self.api = CustomAPI(self.jwt)
        self.rest = Rest(self.api)
        self.api_controller = ApiController(self.jwt, self.api, self.rest)
        self.airflow_controller = AirflowController(self.jwt)

        self.socket_manager = None

    def setup_routes(self, app: FastAPI):
        """
        Override only the React routes, keeping others from the base class.
        """
        # Keep existing route setups
        setup_api_routes(app, self.api_controller, self.jwt)
        setup_socket_routes(app, self.socket_controller)
        setup_setup_routes(app, self.setup_controller)

        # Use custom React routes instead of the default ones
        setup_react_routes(app)      

        # Add custom Airflow routes
        setup_airflow_routes(app, self.airflow_controller, self.jwt)  

# Replace the original BackendAPI with the custom one
backend_api = CustomBackendAPI()

# Override the original FastAPI app
app = FastAPI(
    title="Extended Liberty Airflow",
    description="Extended API with Custom Features",
    version="1.0.1",
    docs_url="/api/test",
    redoc_url="/api",
    openapi_url="/custom-liberty-api.json"
)

# Initialize BackendAPI and register routes and sockets
backend_api = CustomBackendAPI()
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
        start_airflow()
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
    fastapi_host = os.getenv("FASTAPI_HOST", "localhost")  
    fastapi_port = os.getenv("FASTAPI_PORT", 8082)
    
    config = uvicorn.Config("liberty.scheduler.main:app", host=fastapi_host, port=fastapi_port, reload=True, log_level="warning")
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