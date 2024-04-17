from app.stations.data.models import (
    StationData,
    StationDataRead,
    StationDataCreate,
    StationDataUpdate,
)
from sqlmodel_react_admin.routers import ReactAdminRouter
from app.db import engine

station_data_router = ReactAdminRouter(
    db_model=StationData,
    create_model=StationDataCreate,
    read_model=StationDataRead,
    update_model=StationDataUpdate,
    name_singular="station data",
    prefix="/data",
    db_engine=engine,
)
