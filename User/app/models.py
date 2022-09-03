# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Optional, Union

from bson.objectid import ObjectId
from pydantic import BaseModel, validator


class User(BaseModel):
    name: str
    age: int


class CreateUser(User):
    pass


class UpdateUser(User):
    pass


class UserResponse(User):
    id: Union[ObjectId, str]

    @validator("id")
    def id_validator(cls, value: Union[ObjectId, str]) -> str:
        if isinstance(value, ObjectId):
            return str(value)
        if isinstance(value, str):
            return value
        raise ValueError(f"Unexpected Type: {type(value)}, only use 'ObjectId' or 'str'")

    class Config:
        fileds = {"id": "_id"}
        arbitrary_types_allowed = True
