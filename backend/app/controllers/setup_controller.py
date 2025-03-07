import logging
logger = logging.getLogger(__name__)

from fastapi import Request
from app.controllers.api_controller import ApiController
from app.utils.jwt import JWT
from app.setup.services.setup import Setup
from app.setup.services.alembic import Alembic

class SetupController:
    def __init__(self, apiController: ApiController,  jwt: JWT):
        self.setup = Setup(apiController, jwt)
        self.alembic = Alembic(apiController, jwt)

    async def install(self, req: Request):
        return await self.setup.install(req)

    async def prepare(self, req: Request):
        return await self.setup.prepare(req)
    
    async def restore(self, req: Request):
        return await self.setup.restore(req)
        
    async def update(self, req: Request):
        return await self.setup.update(req)    
    
    async def repository(self, req: Request):
        return await self.setup.repository(req)        
    
    def upgrade(self, req: Request):
        return self.alembic.upgrade(req)  
    
    def downgrade(self, req: Request):
        return self.alembic.downgrade(req)      
    
    def revision(self, req: Request):
        return self.alembic.revision(req)          
    
    def current(self, req: Request):
        return self.alembic.current(req)           
    
    async def create(self, req: Request):
        return await self.setup.create_database(req)    
    
    async def drop(self, req: Request):
        return await self.setup.drop_database(req)        