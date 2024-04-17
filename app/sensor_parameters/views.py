from app.sensor_parameters.models import (
    SensorParameter,
    SensorParameterCreate,
    SensorParameterRead,
    SensorParameterUpdate,
)
from sqlmodel_react_admin.routers import ReactAdminRouter
from app.db import engine


sensor_parameters = ReactAdminRouter(
    db_model=SensorParameter,
    create_model=SensorParameterCreate,
    read_model=SensorParameterRead,
    update_model=SensorParameterUpdate,
    name_singular="sensor parameter",
    prefix="/sensor_parameters",
    db_engine=engine,
)
