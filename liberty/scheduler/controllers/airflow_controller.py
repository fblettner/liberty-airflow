from fastapi import Request
from liberty.scheduler.utils.jwt import CustomJWT as JWT
from liberty.scheduler.services.airflow_services import AirflowAPI

class AirflowController:
    def __init__(self, jwt: JWT = None):
        self.api = AirflowAPI()
        self.jwt = jwt

    async def dags(self, req: Request, headers: dict):
        return await self.api.dags(req, headers)  
