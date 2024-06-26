from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from uuid import uuid4, UUID
from typing import Any, TYPE_CHECKING
import datetime
from pydantic import field_validator

if TYPE_CHECKING:
    from app.sensors.models import Sensor
    from app.stations.models.station import Station


class StationSensorAssignmentsBase(SQLModel):
    installed_on: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        nullable=False,
    )
    sensor_position: int = Field(
        gt=0,  # Position must be greater than 0 (starts at 1)
        le=24,  # Only 24 positions allowed on a station
        default=None,
        nullable=False,
    )
    station_id: UUID = Field(
        foreign_key="station.id",
        nullable=False,
    )
    sensor_id: UUID | None = Field(
        None,
        foreign_key="sensor.id",
        nullable=True,
    )

    @field_validator("installed_on")
    def remove_timezone(
        cls,
        v: datetime.datetime | None,
    ) -> datetime.datetime | None:
        if v is None:
            return v
        return v.replace(tzinfo=None)


class StationSensorAssignmentsCreate(StationSensorAssignmentsBase):
    pass


class StationSensorAssignmentsRead(StationSensorAssignmentsBase):
    id: UUID
    station: Any
    sensor: Any


class StationSensorAssignmentsUpdate(StationSensorAssignmentsBase):
    pass


class StationSensorAssignments(StationSensorAssignmentsBase, table=True):
    __table_args__ = (
        UniqueConstraint("id", name="station_sensor_id_constraint"),
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

    station: "Station" = Relationship(
        back_populates="sensor_link",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    sensor: "Sensor" = Relationship(
        back_populates="station_link",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
