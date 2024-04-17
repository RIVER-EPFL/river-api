from sqlmodel import SQLModel, Field
from uuid import UUID
from sqlmodel_react_admin.models import ReactAdminDBModel


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
    sensor_id: UUID = Field(
        nullable=False,
        index=True,
    )


class SensorParameter(SensorParameterBase, ReactAdminDBModel, table=True):
    pass


class SensorParameterCreate(SensorParameterBase):
    pass


class SensorParameterRead(SensorParameterBase):
    id: UUID


class SensorParameterUpdate(SensorParameterBase):
    pass
