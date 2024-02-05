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
