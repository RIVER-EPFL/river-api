from fastapi import HTTPException
import base64
import datetime

from app.stations.models import Station
from app.stations.data.models import (
    StationData,
    StationDataRead,
    StationDataCreate,
    StationDataUpdate,
)

from app.db import AsyncSession
from fastapi import HTTPException
from sqlmodel import select
import random
import string


def decode_base64(value: str) -> tuple[bytes, str]:
    """Decode base64 string to csv bytes"""
    # Split the string using the comma as a delimiter
    data_parts = value.split(",")

    # Extract the data type and base64-encoded content
    if "text/csv" in data_parts[0]:
        type = "csv"
    elif "gpx" in data_parts[0]:
        type = "gpx"
    else:
        raise HTTPException(
            status_code=400,
            detail="Only CSV and GPX files are supported",
        )

    base64_content = data_parts[1]
    rawdata = base64.b64decode(base64_content)

    return rawdata, type


def get_unix_time_from_str(input: str) -> datetime.datetime:
    """Takes the first 10 characters of a string and converts to unix timestamp

    The first 10 characters of a string are assumed to be an integer
    representation of a unix timestamp.

    Args:
        time_str (str): A string representation of a unix timestamp

    Returns:
        datetime.datetime: A datetime object
    """

    cut_string = int(input[:10])

    return datetime.datetime.fromtimestamp(
        cut_string, tz=datetime.timezone.utc
    )


def extract_raw_values_from_str(input: str) -> list[int]:
    """Extracts values from a string

    Each representation of a float is a block of four integers. The string
    is to be split in chunks of four, converted to n-integers in a list.

    Args:
        input (str): The full string given by a sensor including the timestamp
        in the first 10 characters

    Returns:
        list[int]: A list of split integers
    """

    cut_string = input[10:]

    if len(cut_string) % 4 != 0:
        raise ValueError(f"The string {cut_string} is not divisible by 4")

    integer_list = []
    for i in range(0, len(cut_string), 4):
        integer_list.append(int(cut_string[i : i + 4]))

    return integer_list


async def parse_station_data(
    stationdata: StationDataCreate, session: AsyncSession
) -> StationDataRead:
    print(stationdata)
    print(stationdata.raw)
    try:
        query = select(Station).where(
            Station.associated_astrocast_device
            == str(stationdata.astrocast_id)
        )

        res = await session.exec(query)
        station = res.one_or_none()

        param_location = []
        for sensor in station.sensors:
            param_location.append(
                (
                    sensor.parameter.acronym,
                    sensor.station_link.sensor_position,
                    sensor.calibrations,
                )
            )

        [print(x) for x in sorted(param_location, key=lambda x: x[1])]

        obj = StationDataRead(
            values=extract_raw_values_from_str(stationdata.raw),
            recorded_at=get_unix_time_from_str(stationdata.raw),
            station=station,
            received_at=datetime.datetime.now().replace(microsecond=0),
        )

        return obj

    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# Function to generate a random 4-character alphabetic ID
def generate_random_id():
    # Use uppercase letters only
    letters = string.ascii_uppercase

    # Generate a 4-character ID
    return "".join(random.choice(letters) for _ in range(4))
