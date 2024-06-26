from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from uuid import uuid4, UUID
import datetime
from app.stations.models import StationSensorAssignments
from app.sensors.models import Sensor, SensorRead


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

    # Load full sensor relationship with all nested relationships
    # (calibrations, sensor_link)
    sensors: list["Sensor"] = Relationship(
        back_populates="stations",
        link_model=StationSensorAssignments,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    sensor_link: list["StationSensorAssignments"] = Relationship(
        back_populates="station",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class StationRead(StationBase):
    id: UUID
    sensors: list["SensorRead"] = []
    sensor_link: list[StationSensorAssignments] = []


class StationCreate(StationBase):
    pass


class StationUpdate(StationCreate):
    pass
