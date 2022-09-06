# -*- coding: utf-8 -*-

from __future__ import annotations

from contextvars import ContextVar
from os import environ
from uuid import uuid4

import uvicorn
from conf import config
from fastapi import FastAPI, Request, Response, status
from router import router
from starlette.middleware.base import DispatchFunction

ALLOW_METHOD_LIST = ["GET", "POST", "PATCH", "DELETE"]
ENV = environ.get("ENV", "prod")
reload = ENV == "dev"
cfg = config("server")

app = FastAPI(title="User Service", version="1.0.0")

app.include_router(router, prefix="/api/v1")

request_id_contextvar = ContextVar("request_id", default="")


@app.middleware("http")
async def check_authorization(request: Request, call_next: DispatchFunction) -> Response:
    request_id = str(uuid4())
    request_id_contextvar.set(request_id)
    method = request.scope.get("method", "")
    if method not in ALLOW_METHOD_LIST:
        return Response(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id_contextvar.get()
    return response


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=reload)
