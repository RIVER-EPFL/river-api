from sqlmodel import SQLModel, Field, UniqueConstraint, Relationship
import datetime
from uuid import uuid4, UUID
from pydantic import field_validator
from app.stations.models import Station
from app.station_sensors.models import StationSensorAssignments


class SensorBase(SQLModel):
    parameter_name: str | None
    parameter_acronym: str | None
    parameter_unit: str | None
    parameter_db_name: str | None
    serial_number: str | None
    model: str | None
    calibrated_on: datetime.datetime | None

    @field_validator("calibrated_on")
    def remove_timezone(
        cls,
        v: datetime.datetime | None,
    ) -> datetime.datetime | None:
        if v is None:
            return v
        return v.replace(tzinfo=None)


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
    stations: list[Station] = Relationship(
        back_populates="sensors",
        link_model=StationSensorAssignments,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    station_link: StationSensorAssignments = Relationship(
        back_populates="sensor",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class SensorCreate(SensorBase):
    pass


class SensorRead(SensorBase):
    id: UUID
    station_link: StationSensorAssignments | None = None


class SensorUpdate(SensorBase):
    pass
