from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from typing import TYPE_CHECKING
from sqlmodel_react_admin.models import ReactAdminDBModel

# if TYPE_CHECKING:
from app.sensors.models import Sensor, SensorRead


class SensorParameterBase(SQLModel):
    name: str = Field(
        nullable=False,
        index=True,
    )
    acronym: str = Field(
        nullable=False,
        index=True,
    )
    unit: str = Field(
        nullable=False,
        index=True,
    )


class SensorParameter(SensorParameterBase, ReactAdminDBModel, table=True):
    sensors: list["Sensor"] = Relationship(
        back_populates="parameter", sa_relationship_kwargs={"lazy": "selectin"}
    )


class SensorParameterCreate(SensorParameterBase):
    pass


class SensorParameterRead(SensorParameterBase):
    id: UUID
    sensors: list["SensorRead"] = []


class SensorParameterUpdate(SensorParameterBase):
    pass
