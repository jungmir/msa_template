# coding=utf-8

from __future__ import annotations

from os import environ

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from router import router

ENV = environ.get("ENV", "prod")
reload = ENV == "dev"

app = FastAPI(title="User Service", version="1.0.0")

app.include_router(router, prefix="/api/v1/user")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=reload)
