from sqlmodel import SQLModel
from uuid import UUID
import datetime


class AstrocastMessage(SQLModel):
    messageGuid: UUID | None
    deviceGuid: UUID | None
    createdDate: datetime.datetime | None
    receivedDate: datetime.datetime | None
    latitude: float | None
    longitude: float | None
    data: str | None
    messageSize: int | None
    callbackDeliveryStatus: str | None
