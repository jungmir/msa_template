# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict

from conf import config
from fastapi import APIRouter, Depends, Header, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from httpx import AsyncClient
from models import Token, UserData

router = APIRouter()
cfg = config("server")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def generate_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> JSONResponse:
    response: Dict[str, Any] = {}
    async with AsyncClient() as client:
        resp = await client.get(cfg.user.url, params=dict(user_id=form_data.username))
    if resp.status_code != status.HTTP_200_OK:
        return Response(status_code=resp.status_code)
    json = resp.json()
    user = UserData(**json.get("result"))
    if form_data.password != user.password:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)
    token = Token.generate(user)
    print(token)
    response.update(result=token)
    return JSONResponse(content=jsonable_encoder(response))


@router.head("/verify", status_code=status.HTTP_200_OK)
async def verify_token(authorization: str = Header()) -> Response:
    if not Token.verify(authorization):
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)
    return Response()
