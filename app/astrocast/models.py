from sqlmodel import SQLModel, Field, Column, Relationship, UniqueConstraint
from uuid import UUID
import datetime
from uuid import uuid4, UUID


class AstrocastMessageBase(SQLModel):
    requested_at: datetime.datetime = (
        Field(  # When we retrieved the message from the Astrocast API
            index=True,
            nullable=False,
        )
    )

    # Astrocast API fields
    messageGuid: UUID | None
    deviceGuid: UUID | None
    createdDate: datetime.datetime | None
    receivedDate: datetime.datetime | None
    latitude: float | None
    longitude: float | None
    data: str | None
    messageSize: int | None
    callbackDeliveryStatus: str | None


class AstrocastMessage(AstrocastMessageBase, table=True):
    __table_args__ = (UniqueConstraint("messageGuid"),)
    iterator: int = Field(  # Our DB iterator
        default=None,
        nullable=False,
        primary_key=True,
        index=True,
    )
    id: UUID = Field(  # Our UUID of the message
        default_factory=uuid4,
        index=True,
        nullable=False,
    )


class AstrocaseMessageCreate(AstrocastMessageBase):
    pass


class AstrocastMessageRead(AstrocastMessageBase):
    id: UUID
