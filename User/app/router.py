# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from typing import Any, Dict, Union

import httpx
from conf import config
from database import Mongo
from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import CreateUser, SimpleUser, UpdateUser, User, UserRole

router = APIRouter()
cfg = config("server")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token", scheme_name="Bearer")


async def is_verify(token: str) -> Dict[str, Any]:
    headers = {"Authorziation": token}
    async with httpx.AsyncClient() as client:
        resp = await client.get(cfg.auth.verify_url, headers=headers)
    if resp.status_code == status.HTTP_401_UNAUTHORIZED:
        raise HTTPException(status_code=resp.status_code, detail="Invalid token")
    return resp.headers.get("user", {})


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = await is_verify(token)
    _id = payload.get("sub", "")
    mongo = Mongo()
    with mongo("user") as user_database:
        user = user_database.find_by_id(_id)
    return User(**user)


# not required JWT
@router.post("/token", status_code=status.HTTP_200_OK)
async def issued_token_for_authentication(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Response:
    response: Dict[str, Any] = {}
    mongo = Mongo()
    with mongo("user") as user_database:
        query = dict(user_id=form_data.username)
        user = user_database.find(query)
    if not user:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    if form_data.password != user["password"]:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    with httpx.Client() as client:
        data = SimpleUser(sub=user.get("_id"), role=user.get("role")).dict()
        resp = client.post(
            cfg.auth.url,
            headers={"Content-Type": "application/json"},
            json=data,
        )
        if resp.status_code != status.HTTP_201_CREATED:
            return JSONResponse(
                content=jsonable_encoder(resp.json()), status_code=resp.status_code
            )
        response_json = resp.json()
        token = response_json.get("result", {}).get("token")
        response.update(result=token)
        return JSONResponse(content=jsonable_encoder(response))


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUser = Body()) -> JSONResponse:
    response: Dict[str, Any] = {}
    mongo = Mongo()
    with mongo("user") as user_database:
        user_database.insert(user.dict())
    response.update(result={"status": "success"})
    return JSONResponse(content=jsonable_encoder(response))


# required JWT
@router.get("/users/me", status_code=status.HTTP_200_OK)
async def get_self(me: User = Depends(get_current_user)) -> JSONResponse:
    return JSONResponse(content=jsonable_encoder(me))


@router.get("/users")
async def get_all_users(me: User = Depends(get_current_user)) -> JSONResponse:
    response: Dict[str, Any] = {}
    mongo = Mongo()
    with mongo("user") as user_database:
        all_users = user_database.finds()
    response.update(result=all_users)
    return JSONResponse(content=jsonable_encoder(response))


@router.get("/users/{id}", status_code=status.HTTP_200_OK)
async def get_user(id: str, me: User = Depends(get_current_user)) -> JSONResponse:
    response: Dict[str, Any] = {}
    mongo = Mongo()
    with mongo("user") as user_database:
        user = user_database.find_by_id(id)
    response.update(result=user)
    return JSONResponse(content=jsonable_encoder(response))


@router.patch("/users/{id}", status_code=status.HTTP_205_RESET_CONTENT)
async def update_user(
    id: str, user: UpdateUser = Body(), me: User = Depends(get_current_user)
) -> JSONResponse:
    response: Dict[str, Any] = {}
    mongo = Mongo()
    with mongo("user") as user_database:
        matched, modified = user_database.update_by_id(id, user.dict())
    if matched == 0:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    response.update(result={"matched": matched, "modified": modified})
    return JSONResponse(content=jsonable_encoder(response))


@router.delete("/users/{id}", status_code=status.HTTP_205_RESET_CONTENT)
async def delete_user(id: str, me: User = Depends(get_current_user)) -> JSONResponse:
    response: Dict[str, Any] = {}
    mongo = Mongo()
    with mongo("user") as user_database:
        deleted = user_database.delete_by_id(id)
    response.update(result={"deleted": deleted})
    return JSONResponse(content=jsonable_encoder(response))
