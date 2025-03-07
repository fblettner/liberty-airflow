
import os
from fastapi import HTTPException, Request
import requests


class AirflowAPI: 

    async def dags(self, req: Request, headers: dict):
        try: 
            airflow_url = os.getenv("AIRFLOW__WEBSERVER__BASE_URL")  # Default to current directory
            response = requests.get(f"{airflow_url}/api/v1/dags", headers=headers)
            return response.json()
            
        except Exception as err:
            raise HTTPException(status_code=500, detail=str(err))