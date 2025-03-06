from fastapi import HTTPException, Request
from app.utils.jwt import JWT
from app.services.api_services import API
from app.utils.encrypt import Encryption
from app.services.rest_services import Rest

class ApiController:
    def __init__(self, jwt: JWT):
        self.jwt = jwt
        self.api = API(jwt)
        self.rest = Rest(self.api)

    async def token(self, req: Request):
        return await self.api.token(req)

    async def user(self, req: Request):
        return await self.api.user(req)    

    async def encrypt(self, req: Request):
        try:
            data = await req.json()
            plain_text = data.get("plain_text")
            encryption = Encryption(self.jwt)
            encrypted_text = encryption.encrypt_text(plain_text)
            return {"encrypted": encrypted_text}
        except Exception as err:
            raise HTTPException(status_code=500, detail=str(err))

    async def modules(self, req: Request):
        return await self.api.modules(req)
    
    async def applications(self, req: Request):
        return await self.api.applications(req)    
        
    def get_pool_info(self, req: Request, pool: str):
        return self.api.get_pool_info(req, pool)
    
    async def push_log(self, req: Request):
        return await self.rest.push_log(req)    

    async def get_log(self, req: Request):
        return await self.rest.get_log(req) 
    
    async def get_log_details(self, req: Request):
        return await self.rest.get_log_details(req) 


    async def dags(self, req: Request, headers: dict):
        return await self.api.dags(req, headers)  
    
