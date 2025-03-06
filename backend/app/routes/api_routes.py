#
# Copyright (c) 2025 NOMANA-IT and/or its affiliates.
# All rights reserved. Use is subject to license terms.
#
#
import json
from typing import Any, Dict, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, Path
from pydantic import Field
from app.utils.jwt import JWT
from app.controllers.api_controller import ApiController
from app.models.auth import TOKEN_ERROR_MESSAGE, TOKEN_RESPONSE_DESCRIPTION, TOKEN_RESPONSE_EXAMPLE, LoginRequest, TokenResponse
from app.models.base import ErrorResponse, response_200, response_422, response_500
from app.services.api_services import LoginType

def setup_api_routes(app, controller: ApiController, jwt: JWT):
    router = APIRouter()

    @router.post(
        "/auth/token",
        summary="AUTH - Token",
        description="Generate a JWT token for the user.",
        tags=["Authentication"], 
        response_model=TokenResponse,
        responses={
            200: response_200(TokenResponse, TOKEN_RESPONSE_DESCRIPTION, TOKEN_RESPONSE_EXAMPLE),
            422: response_422(),  
            500: response_500(ErrorResponse, TOKEN_ERROR_MESSAGE),
        },
    )
    async def token(
        req: Request,
        body: LoginRequest,
        type: LoginType = Query(None, description="Authentication type, from database or using OIDC. Valid values: `database`, `oidc`, `airflow`"),
    ):
        return await controller.token(req)


    
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