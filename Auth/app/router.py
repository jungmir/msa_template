# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Dict

from conf import config
from fastapi import APIRouter, Body, Header, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from models import SimpleUser, Token

router = APIRouter()
cfg = config("server")


@router.post("", status_code=status.HTTP_201_CREATED)
async def generate_token(
    user: SimpleUser = Body(),
) -> JSONResponse:
    response: Dict[str, Any] = {}
    token = Token.generate(user)
    response.update(result=token)
    return JSONResponse(
        content=jsonable_encoder(response), status_code=status.HTTP_201_CREATED
    )


@router.get("/verify", status_code=status.HTTP_200_OK)
async def verify_token(authorization: str = Header()) -> Response:
    token_type, access_token = authorization.split()
    token = Token(type=token_type, access_token=access_token)
    if not token.verify():
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)
    return Response(status_code=status.HTTP_200_OK)
