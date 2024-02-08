from fastapi import FastAPI, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.config import config
from app.stations.views import router as stations_router
from app.astrocast.views import router as astrocast_router
from app.astrocast.classes import astrocast_api
from pydantic import BaseModel
from contextlib import asynccontextmanager
import asyncio


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    print("Starting up RIVER-API...")

    # Start polling the Astrocast API for messages
    asyncio.create_task(astrocast_api.update_device_types())
    asyncio.create_task(astrocast_api.start_collecting_messages())

    yield


app = FastAPI(
    lifespan=lifespan,
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.add_event_handler("startup", on_startup)


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


@app.get(
    "/healthz",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    Endpoint to perform a healthcheck on for kubenernetes liveness and
    readiness probes.
    """
    return HealthCheck(status="OK")


app.include_router(
    stations_router,
    prefix=f"{config.API_V1_PREFIX}/stations",
    tags=["stations"],
)
app.include_router(
    astrocast_router,
    prefix=f"{config.API_V1_PREFIX}/astrocast",
    tags=["astrocast"],
)
