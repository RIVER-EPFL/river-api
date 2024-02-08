from sqlmodel import SQLModel, Field, Column, Relationship, UniqueConstraint
from geoalchemy2 import Geometry
from uuid import uuid4, UUID
from typing import Any
import datetime


class StationBase(SQLModel):
    name: str = Field(default=None, index=True)
    description: str | None = Field(default=None)
    comment: str | None = Field(default=None)
    time_added_utc: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
        nullable=True,
        index=True,
    )
    associated_astrocast_device: str | None = Field(default=None)


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
    geom: Any = Field(sa_column=Column(Geometry("POINT", srid=4326)))


class StationRead(StationBase):
    id: UUID
    geom: Any


class StationCreate(StationBase):
    pass


class StationUpdate(StationCreate):
    pass
