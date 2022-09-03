# coding=utf-8

from os import environ

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from router import router

PORT = int(environ.get("PORT", 8080))
ENV = environ.get("ENV", "prod")
reload = ENV == "dev"

app = FastAPI(title="User Service", version="1.0.0")

app.include_router(router, prefix="/api/v1/user")

if __name__ == "__main__":
    uvicorn.run("main:app", port=PORT, host="0.0.0.0", reload=reload)
