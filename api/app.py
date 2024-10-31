import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from tortoise.contrib.fastapi import register_tortoise

from starlette.responses import JSONResponse

from api.config import TORTOISE_ORM, debug
from api.errors import APIException
from api.routes import router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,%(msecs)03d %(levelname)s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
)

app_base = "/api/v1"

app = FastAPI(
    title=f"backend API by Architec.TON ",
    debug=debug,
    docs_url=f"{app_base}/docs",
    redoc_url=None,
    version="0.2.0",
    openapi_url=f"{app_base}/backend.json",
)

register_tortoise(app, generate_schemas=True, add_exception_handlers=True, config=TORTOISE_ORM)


@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )
    
    

app.include_router(router, prefix=app_base)

app.add_middleware(
    CORSMiddleware,
    allow_origins='*',  # Update domain.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
