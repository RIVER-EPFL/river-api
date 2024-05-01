import datetime
import pytest
import csv
import os
from app.tests.conftest import EXAMPLE_DATA_DIR


@pytest.fixture()
def sensor_data_6h() -> list[dict[str, str]]:
    """Sensor data at 6h intervals in ascii representations"""
    with open(
        os.path.join(EXAMPLE_DATA_DIR, "ts_6h.csv"),
    ) as f:
        reader = csv.DictReader(f)
        return list(reader)


@pytest.fixture()
def data_message() -> tuple[str, list[int], datetime.datetime]:
    """Example data message from an Astrocast message"""

    return (
        "15799968000445225100030027038822980099008105110000",
        [445, 2251, 3, 27, 388, 2298, 99, 81, 511, 0],
        datetime.datetime(2020, 1, 26, 0, 0, tzinfo=datetime.timezone.utc),
    )
