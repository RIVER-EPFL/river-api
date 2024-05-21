import pytest
import datetime
from uuid import uuid4
from app.sensors.models import Sensor, SensorCreate, SensorRead
from app.stations.models import (
    Station,
    StationSensorAssignments,
    StationSensorAssignmentsCreate,
)
from app.config import config


@pytest.mark.asyncio
async def test_sensor_assignments(client, async_session):
    # Create a station
    station_id = uuid4()
    new_station = Station(id=station_id, name="Test Station")
    async_session.add(new_station)
    await async_session.commit()

    # Create a sensor
    sensor_id = uuid4()
    new_sensor = Sensor(
        id=sensor_id,
        serial_number="12345",
        model="XYZ",
        parameter_id=uuid4(),
        field_id="ABCD",
    )
    async_session.add(new_sensor)
    await async_session.commit()

    # Assign sensor to a position at the station
    assignment1 = StationSensorAssignments(
        sensor_id=sensor_id,
        station_id=station_id,
        sensor_position=1,
        installed_on=datetime.datetime(2024, 1, 1, 10, 0),
    )
    async_session.add(assignment1)
    await async_session.commit()

    # Move sensor to a different position
    assignment2 = StationSensorAssignments(
        sensor_id=sensor_id,
        station_id=station_id,
        sensor_position=2,
        installed_on=datetime.datetime(2024, 1, 2, 10, 0),
    )
    async_session.add(assignment2)
    await async_session.commit()

    # Remove sensor from the station
    removal = StationSensorAssignments(
        sensor_id=None,
        station_id=station_id,
        sensor_position=2,
        installed_on=datetime.datetime(2024, 1, 3, 10, 0),
    )
    async_session.add(removal)
    await async_session.commit()

    # Fetch the sensor to check historical assignments
    response = client.get(f"{config.API_V1_PREFIX}/sensors/{sensor_id}")
    assert response.status_code == 200

    sensor_data = response.json()
    assert "history" in sensor_data

    history = sensor_data["history"]
    assert len(history) == 2

    assert history[0]["from"] == "2024-01-02T10:00:00"
    assert history[0]["to"] == "2024-01-03T10:00:00"
    assert history[0]["station_id"] == str(station_id)
    assert history[0]["sensor_position"] == 2

    assert history[1]["from"] == "2024-01-01T10:00:00"
    assert history[1]["to"] == "2024-01-02T10:00:00"
    assert history[1]["station_id"] == str(station_id)
    assert history[1]["sensor_position"] == 1
