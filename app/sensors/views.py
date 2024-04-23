from app.sensors.models import (
    SensorRead,
    Sensor,
    SensorCreate,
    SensorUpdate,
)
from app.db import async_session
from sqlmodel_react_admin.routers import ReactAdminRouter


router = ReactAdminRouter(
    db_model=Sensor,
    create_model=SensorCreate,
    read_model=SensorRead,
    update_model=SensorUpdate,
    name_singular="sensor",
    prefix="/sensors",
    db_sessionmaker=async_session,
)
