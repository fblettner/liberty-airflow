from fastapi import HTTPException, Request
from app.utils.jwt import JWT
from app.services.api_services import API

class ApiController:
    def __init__(self, jwt: JWT):
        self.jwt = jwt
        self.api = API(jwt)

    async def token(self, req: Request):
        return await self.api.token(req)
    
    async def dags(self, req: Request, headers: dict):
        return await self.api.dags(req, headers)  