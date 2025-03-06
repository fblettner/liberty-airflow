import base64
import logging
import os
logger = logging.getLogger(__name__)

import requests
from werkzeug.security import check_password_hash
from enum import Enum
from fastapi import Request, HTTPException
from app.utils.jwt import JWT
from app.services.db_pool import DBPool, DBType, PoolInterface
from app.utils.common import PoolConfig
from app.utils.encrypt import Encryption

class LoginType(str, Enum):
    database = "database"
    oidc = "oidc"
    airflow = "airflow"

class SessionMode(str, Enum):
    framework = "framework"
    session = "session"


defaultPool = "airflow"

class API:

    def __init__(self, jwt : JWT):
        self.jwt = jwt
        self.db_pools = PoolInterface()

    def load_db_properties(self) -> PoolConfig:
        # Read the properties file
        postgres_host = os.getenv("POSTGRES_HOST", "localhost")
        postgres_port = os.getenv("POSTGRES_PORT", "5432")
        postgres_db = os.getenv("POSTGRES_DB", "airflow")
        postgres_user = os.getenv("POSTGRES_USER", "airflow")
        postgres_password = os.getenv("POSTGRES_PASSWORD", "airflow")

        # Return as a dictionary
        return {
            "user": postgres_user,
            "password": postgres_password,
            "host": postgres_host,
            "port": postgres_port,
            "database": postgres_db,
            "poolMin": 1,
            "poolMax": 10,
            "pool_alias": "airflow",
            "replace_null": "N"
        }

    async def default_pool(self, config) -> PoolConfig:
    # Read the properties file
        
        # Startup logic
        default_pool = DBPool(debug_mode=False)
        await default_pool.create_pool(DBType.POSTGRES, config)
        self.db_pools.add_pool(defaultPool, default_pool)
                                 
        logger.info("Database pool initialized")
    
        
        
    async def token(self, req: Request):
        try: 
            data = await req.json()
            user = data.get("user")
            password = data.get("password")

            context = {
                "where": {
                    "username": user,
                },
                "row_offset": 0,
                "row_limit": 1000,
            }

            user_data = await self.db_pools.get_pool(defaultPool).db_dao.get([["SELECT username, password, first_name, email FROM ab_user where username = :username", None]], context)
            if not user_data:
                return {
                    "access_token": "", 
                    "token_type": "bearer",
                    "status": "failed",
                    "message": "Invalid User"
                }

            stored_hashed_password = user_data["rows"][0]["PASSWORD"]

            # Check if entered password matches the stored hash
            encryption = Encryption(self.jwt)
            if not check_password_hash(stored_hashed_password, encryption.decrypt_text(password)):
                return {
                    "access_token": "", 
                    "token_type": "bearer",
                    "status": "failed",
                    "message": "Invalid Password"
                }

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
    

    async def user(self, req: Request):
        try:
            # Prepare the request and context
            user = req.query_params.get("user")
            context = {
                "where": {
                    "username": user,
                },
                "row_offset": 0,
                "row_limit": 1000,
            }

            user_data = await self.db_pools.get_pool(defaultPool).db_dao.get([["SELECT username, password, first_name, email FROM ab_user where username = :username", None]], context)

            return {
                "items": [{
                    "ROW_ID": user_data["rows"][0]["ROW_ID"],
                    "USR_ID": user_data["rows"][0]["USERNAME"],
                    "USR_PASSWORD": user_data["rows"][0]["PASSWORD"],
                    "USR_NAME": user_data["rows"][0]["FIRST_NAME"],
                    "USR_EMAIL": user_data["rows"][0]["EMAIL"],
                    "USR_STATUS": "Y",
                    "USR_ADMIN": "Y",
                    "USR_LANGUAGE": "en",
                    "USR_MODE": "dark",
                    "USR_READONLY": "N",
                    "USR_DASHBOARD": 1,
                    "USR_THEME": "liberty"
                }],
                "status": "success",
            }

        except Exception as err:
            raise HTTPException(status_code=500, detail=str(err))      
        
    async def dags(self, req: Request, headers: dict):
        try: 
            airflow_url = os.getenv("AIRFLOW__WEBSERVER__BASE_URL")  # Default to current directory
            response = requests.get(f"{airflow_url}/api/v1/dags", headers=headers)
            return response.json()
            
        except Exception as err:
            raise HTTPException(status_code=500, detail=str(err))
 