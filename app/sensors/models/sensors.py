from sqlmodel import SQLModel, Field, UniqueConstraint, Relationship
from uuid import uuid4, UUID
from typing import TYPE_CHECKING
from app.stations.models import StationSensorAssignments
from app.sensors.models.calibrations import (
    SensorCalibration,
    SensorCalibrationRead,
    SensorCalibrationUpdate,
)

if TYPE_CHECKING:
    from app.stations.models import Station
    from app.sensor_parameters.models import SensorParameter


class SensorBase(SQLModel):
    serial_number: str | None
    model: str | None
    parameter_id: UUID = Field(foreign_key="sensorparameter.id")


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
    parameter: "SensorParameter" = Relationship(
        back_populates="sensors",
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
    parameter_id: UUID | None
    station_link: StationSensorAssignments | None = None
    calibrations: list["SensorCalibrationRead"] = []


class SensorUpdate(SensorBase):
    calibrations: list["SensorCalibrationUpdate"]
