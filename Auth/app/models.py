# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime, timedelta
from os import environ
from typing import Any, Dict, Optional, Union
from uuid import uuid4

from conf import config
from jose import JWTError, jwt
from pydantic import BaseModel, Field, validator

cfg = config("token")
TOKEN_TYPE = "Bearer"
ALGORITHM = cfg.algorithm
SECRET = environ.get("SECRET", str(uuid4()))
EXPIRY = timedelta(**cfg.expiry)


class Token(BaseModel):
    access_token: str
    type: str

    @staticmethod
    def generate(user: UserData) -> Token:
        payload = user.dict()
        now = datetime.now()
        expired = now + EXPIRY
        payload.update(exp=expired.timestamp())
        access_token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
        return Token(access_token=access_token, type=TOKEN_TYPE)

    @classmethod
    def verify(cls, authorization: str) -> bool:
        token_type, access_token = authorization.split()
        if token_type != TOKEN_TYPE:
            return False
        try:
            payload = jwt.decode(access_token, SECRET, algorithms=[ALGORITHM])
        except JWTError:
            # invalid token or expired token
            return False
        return True

    @property
    def payload(self) -> Optional[Dict[str, Any]]:
        return jwt.decode(self.access_token, SECRET, algorithms=[ALGORITHM])


class RefreshToken(Token):
    refresh_token: str


class UserData(BaseModel):
    sub: str = Field(alias="_id")
    name: str
    password: str
    role: str

    class Config:
        arbitrary_types_allowed = True


class TokenPayload(UserData):
    iat: float
    exp: float
