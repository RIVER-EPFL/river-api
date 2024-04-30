from sqlmodel import SQLModel, Field, UniqueConstraint
from uuid import uuid4, UUID
import datetime


class StationDataBase(SQLModel):
    time: datetime.datetime = Field(
        ...,
        index=True,
    )
    value: float = Field(
        ...,
        index=True,
    )
    high_resolution: bool = Field(
        ...,
        index=True,
    )
    last_updated: datetime.datetime = Field(
        ...,
        index=True,
    )
    station_id: UUID = Field(
        ...,
        index=True,
    )
    sensor_id: UUID = Field(
        ...,
        index=True,
    )
    parameter_id: UUID = Field(
        ...,
        index=True,
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


class StationDataCreate(StationDataBase):
    pass


class StationDataUpdate(StationDataBase):
    pass
