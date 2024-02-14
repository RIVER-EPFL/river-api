from sqlmodel import SQLModel, Field, UniqueConstraint, Relationship
from uuid import uuid4, UUID
from typing import Any, TYPE_CHECKING
import datetime
from pydantic import field_validator

if TYPE_CHECKING:
    from app.sensors.models import Sensor
    from app.stations.models import Station


class StationSensorAssignmentsBase(SQLModel):
    installed_on: datetime.datetime | None = Field(
        default=None,
        nullable=False,
    )
    sensor_position: int = Field(
        gt=0,  # Position must be greater than 0 (starts at 1)
        le=15,  # Only 15 positions allowed on a station
        default=None,
        nullable=False,
    )
    station_id: UUID = Field(
        foreign_key="station.id",
        nullable=False,
    )
    sensor_id: UUID = Field(
        foreign_key="sensor.id",
        nullable=False,
    )

    @field_validator("installed_on")
    def remove_timezone(
        cls,
        v: datetime.datetime | None,
    ) -> datetime.datetime | None:
        if v is None:
            return v
        return v.replace(tzinfo=None)


# This table assigns a station to a sensor device (SensorDevice), it is a
# many-to-many relationship that defines also the correction parameters for
# the sensor device in the station
class StationSensorAssignments(StationSensorAssignmentsBase, table=True):
    __table_args__ = (
        UniqueConstraint(
            "sensor_position",
            "station_id",
            "sensor_id",
            name="sensor_station_position_unique_constraint",
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

    station: "Station" = Relationship(
        back_populates="sensor_link",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    sensor: "Sensor" = Relationship(
        back_populates="station_link",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class StationSensorAssignmentsCreate(StationSensorAssignmentsBase):
    pass


class StationSensorAssignmentsRead(StationSensorAssignmentsBase):
    id: UUID
    station: Any
    sensor: Any


class StationSensorAssignmentsUpdate(StationSensorAssignmentsBase):
    pass
