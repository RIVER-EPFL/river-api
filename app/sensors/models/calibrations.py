from sqlmodel import SQLModel, Field
import datetime
from pydantic import field_validator, model_validator
from typing_extensions import Self
from typing import Any


class SensorCalibrationBase(SQLModel):
    calibrated_on: datetime.datetime = Field(
        nullable=False,
        index=True,
    )
    slope: float = Field(
        nullable=False,
    )
    intercept: float = Field(
        nullable=False,
    )
    min_range: float = Field(
        nullable=False,
    )
    max_range: float = Field(
        nullable=False,
    )


class SensorCalibrationCreate(SensorCalibrationBase):
    calibrated_on: str

    @model_validator(mode="before")
    def remove_timezone(cls, v) -> dict:
        if isinstance(v.get("calibrated_on"), datetime.datetime):
            v["calibrated_on"] = v["calibrated_on"].replace(tzinfo=None)

        return v


class SensorCalibrationRead(SensorCalibrationBase):
    calibrated_on: datetime.datetime


class SensorCalibrationUpdate(SensorCalibrationBase):
    calibrated_on: str

    @model_validator(mode="before")
    def remove_timezone(cls, v) -> dict:
        if isinstance(v.get("calibrated_on"), datetime.datetime):
            v["calibrated_on"] = v["calibrated_on"].replace(tzinfo=None)

        return v
