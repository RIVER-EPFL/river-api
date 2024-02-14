from sqlmodel import SQLModel, Field, Column, Relationship, UniqueConstraint
from uuid import uuid4, UUID
from typing import Any
import datetime


class StationBase(SQLModel):
    name: str = Field(default=None, index=True)
    description: str | None = Field(default=None)
    acronym: str | None = Field(default=None)
    catchment_name: str | None = Field(default=None)
    time_added_utc: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
        nullable=True,
        index=True,
    )

    # Station coordinates (reference system agnostic), just metadata not needed
    # for the actual data collection or mapping purposes
    x_coordinate: float | None = Field(default=None)
    y_coordinate: float | None = Field(default=None)

    # There are 15 possible sensor slots on the station
    # Each slot can have a sensor device associated with it
    sensor_device_1: UUID | None = Field(
        default=None, foreign_key="sensordevice.id"
    )
    sensor_device_2: UUID | None = Field(
        default=None, foreign_key="sensordevice.id"
    )
    sensor_device_3: UUID | None = Field(
        default=None, foreign_key="sensordevice.id"
    )
    sensor_device_4: UUID | None = Field(
        default=None, foreign_key="sensordevice.id"
    )
    sensor_device_5: UUID | None = Field(
        default=None, foreign_key="sensordevice.id"
    )
    sensor_device_6: UUID | None = Field(
        default=None, foreign_key="sensordevice.id"
    )
    sensor_device_7: UUID | None = Field(
        default=None, foreign_key="sensordevice.id"
    )
    sensor_device_8: UUID | None = Field(
        default=None, foreign_key="sensordevice.id"
    )
    sensor_device_9: UUID | None = Field(
        default=None, foreign_key="sensordevice.id"
    )
    sensor_device_10: UUID | None = Field(
        default=None, foreign_key="sensordevice.id"
    )
    sensor_device_11: UUID | None = Field(
        default=None, foreign_key="sensordevice.id"
    )
    sensor_device_12: UUID | None = Field(
        default=None, foreign_key="sensordevice.id"
    )
    sensor_device_13: UUID | None = Field(
        default=None, foreign_key="sensordevice.id"
    )
    sensor_device_14: UUID | None = Field(
        default=None, foreign_key="sensordevice.id"
    )
    sensor_device_15: UUID | None = Field(
        default=None, foreign_key="sensordevice.id"
    )

    # Astrocast device associated with the station

    associated_astrocast_device: str | None = Field(
        default=None,
    )  # Astrocast device ID external (maybe UUID, but str to be safe)


class Station(StationBase, table=True):
    __table_args__ = (UniqueConstraint("id"),)
    iterator: int = Field(
        default=None,
        nullable=False,
        primary_key=True,
        index=True,
    )
    id: UUID = Field(
        default_factory=uuid4,
        index=True,
        nullable=False,
    )


class StationRead(StationBase):
    id: UUID


class StationCreate(StationBase):
    pass


class StationUpdate(StationCreate):
    pass
