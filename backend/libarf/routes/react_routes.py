import os
from fastapi import APIRouter, Request, Response
from fastapi.responses import FileResponse, RedirectResponse
import httpx

from libarf.public import get_frontend_path, get_offline_path


def setup_react_routes(app):
    router = APIRouter()

    @app.get("/", include_in_schema=False)
    async def serve_react_app(request: Request):
        """
        Serve the React app, but redirect to installation if the database is not set up.
        """   
        if getattr(app.state, "offline_mode", False):
            return RedirectResponse(url="/offline")
        
        accept = request.headers.get("accept", "")
        if "text/html" in accept:
            return FileResponse(get_frontend_path())
                
        return {"detail": "Not Found"}, 404


    @app.get("/offline", include_in_schema=False)
    async def serve_react_app(request: Request):
        """
        Serve the React app, but redirect to offline if the database is not set up.
        """
        return FileResponse(get_offline_path())
    
    @app.get("/airflow/{full_path:path}", include_in_schema=False)
    async def redirect_to_airflow():
        """
        Redirect to the Airflow Web UI, using the `AIRFLOW__WEBSERVER__BASE_URL` environment variable.
        """
        airflow_url = os.getenv("AIRFLOW__WEBSERVER__BASE_URL", "http://localhost:8080")
        return RedirectResponse(url=airflow_url)

        
    app.include_router(router)