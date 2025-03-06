from fastapi import HTTPException, Request
from app.utils.jwt import JWT
from app.services.api_services import API
from app.utils.encrypt import Encryption

class ApiController:
    def __init__(self, jwt: JWT):
        self.jwt = jwt
        self.api = API(jwt)

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
            
    async def dags(self, req: Request, headers: dict):
        return await self.api.dags(req, headers)  
    
