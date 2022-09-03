# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Dict

from database import Mongo
from fastapi import APIRouter, Body, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from models import CreateUser, UpdateUser

router = APIRouter()


@router.get("/")
def get_all_users() -> JSONResponse:
    response: Dict[str, Any] = {}
    mongo = Mongo()
    with mongo("user") as user_database:
        all_users = user_database.finds()
    response.update(result=all_users)
    return JSONResponse(content=jsonable_encoder(response))


@router.get("/{id}")
def get_user(id: str) -> JSONResponse:
    response: Dict[str, Any] = {}
    mongo = Mongo()
    with mongo("user") as user_database:
        user = user_database.find_by_id(id)
    response.update(result=user)
    return JSONResponse(content=jsonable_encoder(response))


@router.post("/")
def create_user(user: CreateUser = Body()) -> JSONResponse:
    response: Dict[str, Any] = {}
    mongo = Mongo()
    with mongo("user") as user_database:
        user_database.insert(user.dict())
    response.update(result={"status": "success"})
    return JSONResponse(content=jsonable_encoder(response))


@router.patch("/{id}")
def update_user(id: str, user: UpdateUser = Body()) -> JSONResponse:
    response: Dict[str, Any] = {}
    mongo = Mongo()
    with mongo("user") as user_database:
        matched, modified = user_database.update_by_id(id, user.dict())
    response.update(result={"matched": matched, "modified": modified})
    if matched == 0:
        response.update(error={"message": "Not exist matched item"})
        return JSONResponse(
            content=jsonable_encoder(response), status_code=status.HTTP_404_NOT_FOUND
        )
    return JSONResponse(content=jsonable_encoder(response))
