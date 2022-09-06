# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime, timedelta
from os import environ
from typing import Any, Dict, Optional
from uuid import uuid4

from conf import config
from jose import JWTError, jwt
from pydantic import BaseModel

cfg = config("token")
TOKEN_TYPE = "Bearer"
ALGORITHM = cfg.algorithm
SECRET = environ.get("SECRET", str(uuid4()))
EXPIRY = timedelta(**cfg.expiry)


class Token(BaseModel):
    access_token: str
    type: str

    @staticmethod
    def generate(user: SimpleUser) -> Token:
        payload = user.dict()
        now = datetime.now()
        expired = now + EXPIRY
        payload.update(exp=expired.timestamp(), iat=now.timestamp())
        access_token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
        return Token(access_token=access_token, type=TOKEN_TYPE)

    def verify(self) -> bool:
        if self.type != TOKEN_TYPE:
            return False
        try:
            payload = jwt.decode(self.access_token, SECRET, algorithms=[ALGORITHM])
        except JWTError:
            # invalid token or expired token
            return False
        return True

    @property
    def payload(self) -> Optional[Dict[str, Any]]:
        return jwt.decode(self.access_token, SECRET, algorithms=[ALGORITHM])


class SimpleUser(BaseModel):
    sub: str
    role: str
