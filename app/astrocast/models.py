from sqlmodel import SQLModel, Field, Column, Relationship, UniqueConstraint
import datetime
import base64
from uuid import uuid4, UUID
from pydantic import root_validator


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
    decoded_data: str | None = None

    @root_validator(pre=True)
    def decode_data(cls, values: dict) -> dict:
        """Decode the data in data and place it into decoded_data"""
        if values.get("data") is not None:
            decoded_data = base64.b64decode(values["data"]).decode("utf-8")
            print(decoded_data)

            values = dict(values)  # Make a copy of the values
            values["decoded_data"] = decoded_data

        return values


class AstrocastDeviceSummary(SQLModel):
    id: UUID
    deviceGuid: UUID
    customerGuid: UUID | None
    deviceTypeId: int | None
    summaryDate: datetime.date | None
    messagesCount: int | None
    messagesSize: int | None
    commandsCount: int | None
    commandsSize: int | None

    @root_validator(pre=True)
    def set_device_id_from_guid(cls, values: dict) -> dict:
        """Set the device id from the deviceGuid

        Necessary for react-admin as it always needs an ID field"""
        if values.get("deviceGuid") is not None:
            values = dict(values)
            values["id"] = values["deviceGuid"]

        return values


class AstrocastDevice(SQLModel):
    id: UUID
    deviceGuid: UUID
    name: str | None
    description: str | None
    deviceType: int | None
    deviceTypeName: str | None
    deviceState: int | None
    disabledUntilDate: datetime.datetime | None
    deviceGroupGuid: UUID | None
    modelNumber: str | None
    serialNumber: str | None
    firmwareVersion: str | None
    componentModelNumber: str | None
    componentSerialNumber: str | None
    componentFirmwareVersion: str | None
    protocolVersion: int | None
    lastMessageDate: datetime.datetime | None
    lastCommandDate: datetime.datetime | None
    lastLocationDate: datetime.datetime | None
    fixedGeolocation: bool | None
    lastLatitude: float | None
    lastLongitude: float | None
    registrationEnabled: bool | None
    billingExcluded: bool | None

    @root_validator(pre=True)
    def set_device_id_from_guid(cls, values: dict) -> dict:
        """Set the device id from the deviceGuid

        Necessary for react-admin as it always needs an ID field"""
        if values.get("deviceGuid") is not None:
            values = dict(values)
            values["id"] = values["deviceGuid"]

        return values