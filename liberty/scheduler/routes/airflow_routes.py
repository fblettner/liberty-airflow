#
# Copyright (c) 2025 NOMANA-IT and/or its affiliates.
# All rights reserved. Use is subject to license terms.
#
#
from fastapi import APIRouter, Depends, Request

from liberty.scheduler.utils.jwt import CustomJWT as JWT
from liberty.scheduler.controllers.airflow_controller import AirflowController

def setup_airflow_routes(app, controller: AirflowController, jwt: JWT):
    router = APIRouter()
    
    @router.get("/airflow/dags",
        summary="DAGS - List",
        description="List DAGs in the database.",
        tags=["Airflow"], 
    )
    async def dags(
        req: Request,
        jwt: str = Depends(jwt.is_valid_jwt),
    ):
        headers = {"Authorization": jwt["authorization"]}


        return await controller.dags(req, headers)
    
    app.include_router(router, prefix="/api")    