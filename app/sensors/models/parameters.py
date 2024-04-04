from sqlmodel import SQLModel, Field, UniqueConstraint, Relationship
from uuid import uuid4, UUID
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.sensors.models import Sensor


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


class SensorParameter(SensorParameterBase, table=True):
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
    # sensors: list["Sensor"] = Relationship(
    #     back_populates="parameters",
    #     sa_relationship_kwargs={"lazy": "selectin"},
    # )


class SensorParameterCreate(SensorParameterBase):
    pass


class SensorParameterRead(SensorParameterBase):
    id: UUID
    db_name: str | None


class SensorParameterUpdate(SensorParameterBase):
    pass
