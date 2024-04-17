from sqlmodel import SQLModel, Field, Column
from uuid import uuid4, UUID
from typing import Any
from sqlmodel_react_admin.models import ReactAdminDBModel
import datetime


class StationDataBase(SQLModel):
    time: datetime.datetime = Field(
        ...,
        index=True,
    )
    value: float = Field(
        ...,
        index=True,
    )
    high_resolution: bool = Field(
        ...,
        index=True,
    )
    last_updated: datetime.datetime = Field(
        ...,
        index=True,
    )
    station_id: UUID = Field(
        ...,
        index=True,
    )
    sensor_id: UUID = Field(
        ...,
        index=True,
    )
    parameter_id: UUID = Field(
        ...,
        index=True,
    )


class StationData(StationDataBase, ReactAdminDBModel, table=True):
    pass


class StationDataRead(StationDataBase):
    id: UUID


class StationDataCreate(StationDataBase):
    pass


class StationDataUpdate(StationDataBase):
    pass
