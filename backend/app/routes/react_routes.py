import os
from fastapi import APIRouter, Request, Response
from fastapi.responses import FileResponse, RedirectResponse
import httpx

from app.public import get_frontend_path, get_offline_path


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
    
    @app.api_route("/airflow/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"],  include_in_schema=False)
    async def proxy_airflow(full_path: str, request: Request):
        """
        Serve the Airflow UI through FastAPI by proxying requests.
        """
        airflow_url = os.getenv("AIRFLOW__WEBSERVER__BASE_URL", "http://localhost:8080")
        async with httpx.AsyncClient() as client:
            airflow_url = f"{airflow_url}/{full_path}"
            headers = dict(request.headers)  # Pass all request headers
            body = await request.body()  # Capture request body if needed
            
            response = await client.request(
                method=request.method,
                url=airflow_url,
                headers=headers,
                content=body
            )

        # Serve the response from Airflow back to the client
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )

        
    app.include_router(router)