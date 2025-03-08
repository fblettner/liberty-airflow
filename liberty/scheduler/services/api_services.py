import base64
import os
import logging
logger = logging.getLogger(__name__)

import requests
from fastapi import HTTPException, Request
from werkzeug.security import check_password_hash

from liberty.framework.services.api_services import API  # Import the existing service
from liberty.framework.services.db_pool import DBPool, DBType, PoolConfig
from liberty.framework.utils.encrypt import Encryption
from liberty.scheduler.utils.common import load_env

defaultPool = "default"
airflowPool = "airflow"

class CustomAPI(API): 

    def load_liberty_properties(self) -> PoolConfig:
        # Read the properties file
        load_env() 
        postgres_host = os.getenv("POSTGRES_HOST", "localhost")
        postgres_port = os.getenv("POSTGRES_PORT", "5432")
        postgres_db = os.getenv("POSTGRES_LIBERTY_DB", "liberty")
        postgres_user = os.getenv("POSTGRES_LIBERTY_USER", "liberty")
        postgres_password = os.getenv("POSTGRES_LIBERTY_PASSWORD", "liberty")

        # Return as a dictionary
        return {
            "user": postgres_user,
            "password": postgres_password,
            "host": postgres_host,
            "port": postgres_port,
            "database": postgres_db,
            "poolMin": 1,
            "poolMax": 10,
            "pool_alias": defaultPool,
            "replace_null": "N"
        }

    def load_airflow_properties(self) -> PoolConfig:
        load_env() 
        # Read the properties file
        postgres_host = os.getenv("POSTGRES_HOST", "localhost")
        postgres_port = os.getenv("POSTGRES_PORT", "5432")
        postgres_db = os.getenv("POSTGRES_AIRFLOW_DB", "airflow")
        postgres_user = os.getenv("POSTGRES_AIRFLOW_USER", "airflow")
        postgres_password = os.getenv("POSTGRES_AIRFLOW_PASSWORD", "airflow")

        # Return as a dictionary
        return {
            "user": postgres_user,
            "password": postgres_password,
            "host": postgres_host,
            "port": postgres_port,
            "database": postgres_db,
            "poolMin": 1,
            "poolMax": 10,
            "pool_alias": airflowPool,
            "replace_null": "N"
        }

    async def airflow_pool(self, config) -> PoolConfig:
    # Read the properties file
        
        # Startup logic
        airflow_pool = DBPool(debug_mode=False)
        await airflow_pool.create_pool(DBType.POSTGRES, config)
        self.db_pools.add_pool(airflowPool, airflow_pool)
                                 
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

            user_data = await self.db_pools.get_pool(airflowPool).db_dao.get([["SELECT username, password, first_name, email FROM ab_user where username = :username", None]], context)
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
            decrypt_password = encryption.decrypt_text(password)
            if not check_password_hash(stored_hashed_password, decrypt_password):
                return {
                    "access_token": "", 
                    "token_type": "bearer",
                    "status": "failed",
                    "message": "Invalid Password"
                }

            basic_auth_token = base64.b64encode(f"{user}:{decrypt_password}".encode()).decode()

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

            user_data = await self.db_pools.get_pool(airflowPool).db_dao.get([["SELECT username, password, first_name, email FROM ab_user where username = :username", None]], context)

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
                    "USR_DASHBOARD": None,
                    "USR_THEME": "liberty"
                }],
                "status": "success",
            }

        except Exception as err:
            raise HTTPException(status_code=500, detail=str(err))      
        
