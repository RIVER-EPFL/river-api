from sqlmodel import SQLModel, Field, UniqueConstraint
import datetime
from uuid import uuid4, UUID
from pydantic import validator


class SensorDeviceBase(SQLModel):
    parameter_name: str | None
    parameter_acronym: str | None
    parameter_unit: str | None
    parameter_db_name: str | None
    serial_number: str | None
    model: str | None
    installed_on: datetime.datetime | None
    calibrated_on: datetime.datetime | None

    @validator("installed_on", "calibrated_on", pre=False, always=True)
    def remove_timezone(cls, v):
        if v is None:
            return v
        return v.replace(tzinfo=None)


class SensorDevice(SensorDeviceBase, table=True):
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


class SensorDeviceCreate(SensorDeviceBase):
    pass


class SensorDeviceRead(SensorDeviceBase):
    id: UUID


class SensorDeviceUpdate(SensorDeviceBase):
    pass
