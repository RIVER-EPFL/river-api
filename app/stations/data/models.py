from sqlmodel import SQLModel, Field, UniqueConstraint, Column, JSON
from uuid import uuid4, UUID
from typing import Any
import datetime
from app.stations.models import StationRead
from app.sensors.models.calibrations import (
    SensorCalibrationRead,
    SensorCalibrationUpdate,
    SensorCalibrationCreate,
)


class StationDataBase(SQLModel):
    # The actual data:
    raw_value: int = Field(
        ...,
        index=True,
        description="The raw value given in the portion of the astrocast message",
    )
    corrected_value: float | None = Field(
        None,
        index=True,
        description=(
            "The corrected value from the associated sensor's "
            "calibration parameters"
        ),
    )
    high_resolution: bool = Field(
        ...,
        index=True,
        description=(
            "If the data is high resolution (imported "
            "locally), or low resolution (recevied from Astrocast)"
        ),
    )

    # Data has a relationship to many tables:
    astrocast_message_id: UUID = Field(
        ...,
        index=True,
        description="The Astrocast message that this measurement belongs to",
        foreign_key="astrocastmessage.id",
    )
    station_sensor_id: UUID = Field(
        ...,
        index=True,
        description="The Sensor's Station assignment for this data",
        foreign_key="stationsensorassignments.id",
    )
    sensor_id: UUID = Field(
        ...,
        index=True,
        description="The Sensor's for this data",
        foreign_key="sensor.id",
    )

    # Correction parameter information
    last_corrected_at: datetime.datetime = Field(
        ...,
        index=True,
        description="When the data was last updated from calibration parameters",
    )
    calibration_parameters: SensorCalibrationCreate = Field(
        ...,
        description="The calibration parameters used to correct the raw value",
        sa_column=Column(JSON),
    )


class StationData(StationDataBase, table=True):
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


class StationDataRead(StationDataBase):
    id: UUID


class StationDataCreate(SQLModel):
    raw: str
    astrocast_id: UUID | str
    received_at: datetime.datetime | None = None
    recorded_at: datetime.datetime | None = None
    values: list[int] = []
    parameters: list[str] = []
    station: "StationRead" = None
    astrocast_device: Any = None


class StationDataUpdate(StationDataBase):
    pass


class ControlMessageBase(SQLModel):
    """Control messages

    A control message is sent as the first message after a station starts
    to notify the portal of the locations that the sensor is at.
    """

    message: str
    received_at: datetime.datetime = Field(
        ..., index=True, description="When the control message was received"
    )
    astrocast_message_id: UUID = Field(
        ...,
        index=True,
        description="The Astrocast message that this control message is for",
        foreign_key="astrocastmessage.id",
    )
    station_id: UUID = Field(
        ...,
        index=True,
        description="The station that this control message is for",
        foreign_key="station.id",
    )


class ControlMessage(ControlMessageBase, table=True):
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
