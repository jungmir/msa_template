# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Union

from bson.objectid import ObjectId
from const import Role
from pydantic import BaseModel, Field, validator


class LoginUser(BaseModel):
    user_id: str


class UserRole(BaseModel):
    role: Union[Role, str]

    @validator("role")
    def role_validator(cls, value: Union[Role, str]) -> Role:
        if isinstance(value, Role):
            return value
        if hasattr(Role, value.upper()):
            return getattr(Role, value.upper())
        raise ValueError(f"'{value}' is not support, use only 'admin' or 'user'")


class User(UserRole, LoginUser):
    name: str
    password: str
    age: int
    role: Union[Role, str] = Role.USER


class CreateUser(User):
    pass


class UpdateUser(User):
    pass


class SimpleUser(BaseModel):
    sub: str
    role: str


class UserResponse(User):
    id: Union[ObjectId, str] = Field(alias="_id")

    @validator("id")
    def id_validator(cls, value: Union[ObjectId, str]) -> str:
        if isinstance(value, ObjectId):
            return str(value)
        if isinstance(value, str):
            return value
        raise ValueError(f"Unexpected Type: {type(value)}, only use 'ObjectId' or 'str'")

    class Config:
        arbitrary_types_allowed = True
