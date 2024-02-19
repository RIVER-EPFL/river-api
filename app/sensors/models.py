from sqlmodel import SQLModel, Field, UniqueConstraint, Relationship
import datetime
from uuid import uuid4, UUID
from pydantic import field_validator
from app.station_sensors.models import StationSensorAssignments
from typing import Any, TYPE_CHECKING
from sqlalchemy import case, create_engine, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlmodel import Field, Relationship, Session, SQLModel, select
from pydantic import ConfigDict

if TYPE_CHECKING:
    from app.stations.models import Station


class SensorCalibrationBase(SQLModel):
    calibrated_on: datetime.datetime = Field(
        nullable=False,
        index=True,
    )

    sensor_id: UUID = Field(
        foreign_key="sensor.id",
        nullable=False,
    )
    slope: float = Field(
        nullable=False,
    )
    intercept: float = Field(
        nullable=False,
    )
    min_range: float = Field(
        nullable=False,
    )
    max_range: float = Field(
        nullable=False,
    )

    @field_validator("calibrated_on")
    def remove_timezone(
        cls,
        v: datetime.datetime | None,
    ) -> datetime.datetime | None:
        if v is None:
            return v
        return v.replace(tzinfo=None)


class SensorCalibration(SensorCalibrationBase, table=True):
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

    sensor: "Sensor" = Relationship(
        back_populates="calibrations",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class SensorCalibrationCreate(SensorCalibrationBase):
    pass


class SensorCalibrationRead(SensorCalibrationBase):
    id: UUID


class SensorCalibrationUpdate(SensorCalibrationBase):
    pass


class SensorBase(SQLModel):
    parameter_name: str | None
    parameter_acronym: str | None
    parameter_unit: str | None
    parameter_db_name: str | None
    serial_number: str | None
    model: str | None


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
    stations: list["Station"] = Relationship(
        back_populates="sensors",
        link_model=StationSensorAssignments,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    station_link: StationSensorAssignments = Relationship(
        back_populates="sensor",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    calibrations: list["SensorCalibration"] = Relationship(
        back_populates="sensor",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "order_by": "desc(SensorCalibration.calibrated_on)",
        },
    )  # Must be sorted in desc. order for UI to display the latest calibration


class SensorCreate(SensorBase):
    pass


class SensorRead(SensorBase):
    id: UUID
    station_link: StationSensorAssignments | None = None
    calibrations: list["SensorCalibrationRead"] = []


class SensorUpdate(SensorBase):
    calibrations: list["SensorCalibrationUpdate"]
