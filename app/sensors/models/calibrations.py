from sqlmodel import SQLModel, Field, UniqueConstraint, Relationship
import datetime
from uuid import uuid4, UUID
from pydantic import field_validator
from typing import TYPE_CHECKING
from app.sensors.models.parameters import SensorParameter

if TYPE_CHECKING:
    from app.sensors.models.sensors import Sensor


class SensorCalibrationBase(SQLModel):
    calibrated_on: datetime.datetime = Field(
        nullable=False,
        index=True,
    )

    sensor_id: UUID = Field(
        foreign_key="sensor.id",
        nullable=False,
    )
    # parameter_id: UUID = Field(
    #     foreign_key="sensor_parameter.id",
    #     nullable=False,
    # )
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

    # parameter: "SensorParameter" = Relationship(
    #     back_populates="sensors",
    #     sa_relationship_kwargs={"lazy": "selectin"},
    # )


class SensorCalibrationCreate(SensorCalibrationBase):
    pass


class SensorCalibrationRead(SensorCalibrationBase):
    id: UUID


class SensorCalibrationUpdate(SensorCalibrationBase):
    pass
