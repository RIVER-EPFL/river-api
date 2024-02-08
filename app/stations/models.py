from sqlmodel import SQLModel, Field, Column, Relationship, UniqueConstraint
from geoalchemy2 import Geometry
from uuid import uuid4, UUID
from typing import Any
import datetime


class StationBase(SQLModel):
    name: str = Field(default=None, index=True)
    description: str | None = Field(default=None)
    comment: str | None = Field(default=None)
    time_added_utc: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
        nullable=True,
        index=True,
    )


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
    geom: Any = Field(sa_column=Column(Geometry("POINT", srid=4326)))

    data: list["SensorData"] = Relationship(
        back_populates="station",
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

    station_id: UUID = Field(
        default=None, foreign_key="station.id", nullable=False, index=True
    )

    station: Station = Relationship(
        back_populates="data",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class SensorDataRead(SensorDataBase):
    id: UUID
    sensor_id: UUID


class StationRead(StationBase):
    id: UUID
    geom: Any
    battery_voltage: float | None = Field(default=None)
    healthy: bool | None = Field(default=None)
    temperature_1: float | None = Field(default=None)
    temperature_2: float | None = Field(default=None)
    last_data_utc: datetime.datetime | None = Field(default=None)


class StationCreate(StationBase):
    pass


class StationUpdate(StationCreate):
    instrumentdata: str | None = None


class SensorDataSummary(SQLModel):
    start_date: datetime.datetime | None = None
    end_date: datetime.datetime | None = None
    qty_records: int | None = None


class StationReadWithDataSummary(StationRead):
    data: SensorDataSummary


class StationReadWithDataSummaryAndPlot(StationRead):
    data: SensorDataSummary | None
    temperature_plot: list[SensorDataRead] | None = None
