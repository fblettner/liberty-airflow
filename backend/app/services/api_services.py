import base64
import logging
import os
logger = logging.getLogger(__name__)

from enum import Enum
from fastapi import Request, HTTPException
from app.utils.jwt import JWT
import requests

class LoginType(str, Enum):
    database = "database"
    oidc = "oidc"
    airflow = "airflow"
    
class API:

    def __init__(self, jwt : JWT):
        self.jwt = jwt


    async def token(self, req: Request):
        try: 
            data = await req.json()
            user = data.get("user")
            password = data.get("password")
            basic_auth_token = base64.b64encode(f"{user}:{password}".encode()).decode()

            if user:
                access_token = self.jwt.create_access_token(data={"sub": user}, authorization=f"Basic {basic_auth_token}")

                return {
                    "access_token": access_token, 
                    "token_type": "bearer",
                    "status": "success",
                    "message": "Authentication successful"
                }
            return user
            
        except Exception as err:
            raise HTTPException(status_code=500, detail=str(err))
    
        
    async def dags(self, req: Request, headers: dict):
        try: 
            airflow_url = os.getenv("AIRFLOW__WEBSERVER__BASE_URL")  # Default to current directory
            response = requests.get(f"{airflow_url}/api/v1/dags", headers=headers)
            return response.json()
            
        except Exception as err:
            raise HTTPException(status_code=500, detail=str(err))
 