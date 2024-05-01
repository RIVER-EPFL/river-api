from sqlmodel import (
    SQLModel,
    Field,
    UniqueConstraint,
    Relationship,
    JSON,
    Column,
)
from uuid import uuid4, UUID
from typing import TYPE_CHECKING
from app.stations.models import StationSensorAssignments
from app.sensors.models.calibrations import (
    SensorCalibrationRead,
    SensorCalibrationUpdate,
    SensorCalibrationCreate,
)
from app.sensor_parameters.models import (
    SensorParameter,
    SensorParameterReadWithoutSensors,
)
from typing import Any
from typing_extensions import Self
from pydantic import model_validator

if TYPE_CHECKING:
    from app.stations.models import Station


class SensorBase(SQLModel):
    serial_number: str | None
    model: str | None
    parameter_id: UUID = Field(foreign_key="sensorparameter.id")
    calibrations: list["SensorCalibrationCreate"] = Field(
        default=[], sa_column=Column(JSON)
    )


class Sensor(SensorBase, table=True):
    __table_args__ = (
        UniqueConstraint("id"),
        UniqueConstraint(
            "field_id",
            name="unique_sensor_field_id",
        ),
    )
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
    parameter: SensorParameter = Relationship(
        back_populates="sensors",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    field_id: str = Field(
        nullable=False,
        description="The unique field id of the sensor to be used in the "
        "control message",
    )


class SensorCreate(SensorBase):
    pass


class SensorRead(SensorBase):
    id: UUID
    parameter_id: UUID | None
    parameter: SensorParameterReadWithoutSensors | None = None
    station_link: StationSensorAssignments | None = None
    calibrations: list["SensorCalibrationRead"] = []
    field_id: str | None = None

    @model_validator(mode="after")
    def order_calibrations_by_descending_time(self) -> Self:
        if not self.calibrations:
            return self

        # Sort the data and order by calibrated_on descending

        self.calibrations = sorted(
            self.calibrations,
            key=lambda x: x.calibrated_on,
            reverse=True,
        )
        return self


class SensorUpdate(SensorBase):
    calibrations: list["SensorCalibrationUpdate"]
