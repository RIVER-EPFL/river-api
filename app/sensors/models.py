from sqlmodel import SQLModel, Field, Column, Relationship, UniqueConstraint
from geoalchemy2 import Geometry, WKBElement
from uuid import uuid4, UUID
from typing import Any
from pydantic import validator, root_validator
import shapely
from typing import TYPE_CHECKING
import datetime


class SensorBase(SQLModel):
    name: str = Field(default=None, index=True)
    description: str | None = Field(default=None)
    comment: str | None = Field(default=None)
    time_added_utc: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
        nullable=True,
        index=True,
    )


class Sensor(SensorBase, table=True):
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
    geom: Any = Field(sa_column=Column(Geometry("POINT", srid=4326)))

    data: list["SensorData"] = Relationship(
        back_populates="sensor",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class SensorDataBase(SQLModel):
    instrument_seq: int = Field(  # The iterator integer in the instrument
        index=True,
        nullable=False,
    )
    time: datetime.datetime = Field(
        index=True,
        nullable=False,
    )
    time_zone: int | None = Field(
        index=False,
        nullable=True,
    )
    temperature_1: float | None = Field(
        index=True,
        nullable=True,
    )
    temperature_2: float | None = Field(
        index=True,
        nullable=True,
    )
    temperature_3: float | None = Field(
        index=True,
        nullable=True,
    )
    river_moisture_count: float | None = Field(
        index=True,
        nullable=True,
    )
    shake: int | None = Field(
        index=False,
        nullable=True,
    )
    error_flat: int | None = Field(
        index=False,
        nullable=True,
    )


class SensorData(SensorDataBase, table=True):
    __table_args__ = (UniqueConstraint("id"),)
    iterator: int = Field(
        nullable=False,
        primary_key=True,
        index=True,
    )
    id: UUID = Field(
        default_factory=uuid4,
        index=True,
        nullable=False,
    )

    sensor_id: UUID = Field(
        default=None, foreign_key="sensor.id", nullable=False, index=True
    )

    sensor: Sensor = Relationship(
        back_populates="data",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class SensorDataRead(SensorDataBase):
    id: UUID
    sensor_id: UUID


class SensorRead(SensorBase):
    id: UUID
    geom: Any
    battery_voltage: float | None = Field(default=None)
    healthy: bool | None = Field(default=None)
    temperature_1: float | None = Field(default=None)
    temperature_2: float | None = Field(default=None)
    last_data_utc: datetime.datetime | None = Field(default=None)


class SensorCreate(SensorBase):
    pass


class SensorUpdate(SensorCreate):
    instrumentdata: str | None = None


class SensorDataSummary(SQLModel):
    start_date: datetime.datetime | None = None
    end_date: datetime.datetime | None = None
    qty_records: int | None = None


class SensorReadWithDataSummary(SensorRead):
    data: SensorDataSummary


class SensorReadWithDataSummaryAndPlot(SensorRead):
    data: SensorDataSummary | None
    temperature_plot: list[SensorDataRead] | None = None
