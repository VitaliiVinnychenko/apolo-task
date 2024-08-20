from typing import Any, Callable, Literal

import secure
from elasticapm.contrib.starlette import ElasticAPM, make_apm_client
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routers import nodes, jobs
from app.config import get_settings, Settings
from app.logger import get_logger
from app.utils.helpers import custom_generate_unique_id

settings: Settings = get_settings()
logger = get_logger(__name__)


app = FastAPI(
    root_path=settings.root_path,
    generate_unique_id_function=custom_generate_unique_id,
    docs_url=None if settings.ENV == "prod" else "/docs",
    redoc_url=None if settings.ENV == "prod" else "/redoc",
    openapi_url=None if settings.ENV == "prod" else "/openapi.json",
)

csp = secure.ContentSecurityPolicy().default_src("'self'").frame_ancestors("'none'")
hsts = secure.StrictTransportSecurity().max_age(31536000).include_subdomains()
referrer = secure.ReferrerPolicy().no_referrer()
cache_value = secure.CacheControl().no_cache().no_store().max_age(0).must_revalidate()
x_frame_options = secure.XFrameOptions().deny()

secure_headers = secure.Secure(
    csp=csp,
    hsts=hsts,
    referrer=referrer,
    cache=cache_value,
    xfo=x_frame_options,
)

apm = make_apm_client(
    {
        "SERVICE_NAME": settings.app_name,
        "SERVER_URL": settings.ELASTIC_APM_SERVER_URL,
        "ENABLED": settings.ELASTIC_APM_ENABLED,
        "LOG_LEVEL": settings.ELASTIC_APM_LOG_LEVEL,
        "ENVIRONMENT": settings.ELASTIC_APM_ENVIRONMENT,
        "DEBUG": settings.ELASTIC_APM_DEBUG,
        "TRANSACTIONS_IGNORE_PATTERNS": [
            "/status",
        ],
        "CAPTURE_BODY": settings.ELASTIC_APM_CAPTURE_BODY,
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CLIENT_ORIGIN_URLS.split(","),
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=86400,
)

# Elastic APM instrumentation needs to be added after all the BaseHTTPMiddlewares to mitigate the mutated
# context objects in Starlette
# Caveat: APM instrumentation will lose the span data of the upward middlewares in the stack
app.add_middleware(ElasticAPM, client=apm)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: Any) -> JSONResponse:
    message = str(exc.detail)

    return JSONResponse({"message": message}, status_code=exc.status_code)


@app.middleware("http")
async def set_secure_headers(request: Request, call_next: Callable) -> Response:
    response = await call_next(request)

    if request.url.path in settings.WHITELISTED_PATHS:
        return response

    secure_headers.framework.fastapi(response)
    return response


@app.get("/status", status_code=status.HTTP_200_OK, operation_id="status_200")
async def get_status() -> dict[str, Literal[True]]:
    return {"healthy": True}


@app.get(
    "/error",
    status_code=status.HTTP_200_OK,
    description="""
    This endpoint is for generating 500s to be read by apm.
    All it does it return errors"
    """,
)
async def get_error() -> None:
    raise Exception


app.include_router(nodes.router)
app.include_router(jobs.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
    )
