from app.sensors.models import (
    SensorRead,
    Sensor,
    SensorCreate,
    SensorUpdate,
)
from app.stations.models import StationSensorAssignments
from app.stations.models.station import Station
from app.db import get_session, AsyncSession
from fastapi import Depends, APIRouter, Query, Response, HTTPException
from sqlmodel import select
from uuid import UUID
from typing import Any
from app.crud import CRUD
from app.utils import generate_random_id

router = APIRouter()
crud = CRUD(Sensor, SensorRead, SensorCreate, SensorUpdate)


async def get_count(
    response: Response,
    filter: str = Query(None),
    range: str = Query(None),
    sort: str = Query(None),
    session: AsyncSession = Depends(get_session),
):
    count = await crud.get_total_count(
        response=response,
        sort=sort,
        range=range,
        filter=filter,
        session=session,
    )

    return count


async def get_current_assignment_property(
    sensor: Sensor,
    session: AsyncSession = Depends(get_session),
) -> SensorRead:

    sensor = SensorRead.model_validate(sensor)

    # If the sensor has a station_link, get the most recent by installed_on
    if sensor.station_link:
        print(sensor.station_link)
        station_link = sensor.station_link
        station_link = sorted(
            station_link, key=lambda x: x.installed_on, reverse=True
        )

        # Query the station for the current assignment at the position in the
        # station link
        query = await session.exec(
            select(StationSensorAssignments)
            .where(
                StationSensorAssignments.station_id
                == station_link[0].station_id
            )
            .where(
                StationSensorAssignments.sensor_position
                == station_link[0].sensor_position
            )
            .order_by(StationSensorAssignments.installed_on.desc())
            .limit(1)
        )
        station_assingment_res = query.one_or_none()

        if station_assingment_res.sensor_id == sensor.id:
            sensor.current_assignment = station_link[0]

    return sensor


async def get_historical_assignments(
    sensor: Sensor,
    session: AsyncSession = Depends(get_session),
) -> SensorRead:
    """Returns a list of historical assignments with from and to dates"""
    sensor = SensorRead.model_validate(sensor)

    if sensor.station_link:
        # Query all assignments for the sensor, including where sensor_id is None
        query = await session.exec(
            select(StationSensorAssignments, Station.name)
            .where(
                (StationSensorAssignments.sensor_id == sensor.id)
                | (StationSensorAssignments.sensor_id == None)
            )
            .join(Station, StationSensorAssignments.station_id == Station.id)
            .order_by(StationSensorAssignments.installed_on.asc())
        )
        assignments = query.all()

        # Process the assignments to include "to" dates
        history = []
        previous_assignment = None

        for i, (assignment, station_name) in enumerate(assignments):
            if previous_assignment:
                if (
                    assignment.sensor_id is None
                    or assignment.sensor_id != sensor.id
                ) and assignment.sensor_position == previous_assignment[
                    "sensor_position"
                ]:
                    # Set "to" date if the next assignment is a removal or different sensor assignment at the same position
                    previous_assignment["to"] = assignment.installed_on

                elif (
                    assignment.sensor_id == sensor.id
                    and assignment.sensor_position
                    != previous_assignment["sensor_position"]
                ):
                    # Set "to" date if the sensor is moved to a different position within the same station
                    previous_assignment["to"] = assignment.installed_on

            if assignment.sensor_id == sensor.id:
                history.append(
                    {
                        "from": assignment.installed_on,
                        "to": None,  # Initialize to None, will be set by the next iteration
                        "station_id": assignment.station_id,
                        "station_name": station_name,
                        "sensor_position": assignment.sensor_position,
                    }
                )
                previous_assignment = history[-1]
            elif assignment.sensor_id is None and previous_assignment:
                # This indicates the sensor was removed from its position
                if (
                    assignment.sensor_position
                    == previous_assignment["sensor_position"]
                ):
                    previous_assignment["to"] = assignment.installed_on
                    previous_assignment = None  # Reset previous assignment

        # If the last assignment is still active, its "to" date should remain None
        if previous_assignment and previous_assignment["to"] is None:
            previous_assignment["to"] = (
                None  # Ensure it's explicitly set to None
            )

        # Sort history by "from" date descending
        sensor.history = sorted(history, key=lambda x: x["from"], reverse=True)

    return sensor


async def get_data(
    filter: str = Query(None),
    sort: str = Query(None),
    range: str = Query(None),
    session: AsyncSession = Depends(get_session),
):
    res = await crud.get_model_data(
        sort=sort,
        range=range,
        filter=filter,
        session=session,
    )
    updated_sensors = []
    for sensor in res:
        sensor = await get_current_assignment_property(sensor, session=session)
        updated_sensors.append(sensor)

    return updated_sensors


async def get_one(
    sensor_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    res = await crud.get_model_by_id(model_id=sensor_id, session=session)

    obj = await get_current_assignment_property(res, session=session)
    obj = await get_historical_assignments(obj, session=session)

    return obj


@router.get("/{sensor_id}", response_model=SensorRead)
async def get_sensor(
    obj: CRUD = Depends(get_one),
) -> SensorRead:
    """Get a sensor by id"""

    return obj


@router.get("", response_model=list[SensorRead])
async def get_all_sensors(
    response: Response,
    sensors: CRUD = Depends(get_data),
    total_count: int = Depends(get_count),
) -> list[SensorRead]:
    """Get all sensor data"""

    return sensors


@router.post("", response_model=SensorRead)
async def create_sensor(
    sensor: SensorCreate,
    session: AsyncSession = Depends(get_session),
) -> SensorRead:
    """Creates a sensor data record"""

    # Get all of the field_ids
    query = await session.exec(select(Sensor.field_id))
    existing_field_ids = query.all()

    # Generate a random field_id
    field_id = generate_random_id()
    while field_id in existing_field_ids:
        field_id = generate_random_id()

    # Add field ID to the sensor data
    sensor_data_dict = sensor.model_dump()
    sensor_data_dict["field_id"] = field_id

    obj = Sensor.model_validate(sensor_data_dict)

    session.add(obj)
    await session.commit()
    await session.refresh(obj)

    return obj


@router.put("/{sensor_id}", response_model=Any)
async def update_sensor(
    sensor_id: UUID,
    sensor_update: SensorUpdate,
    session: AsyncSession = Depends(get_session),
) -> SensorRead:
    """Update a sensor by id"""

    res = await session.exec(select(Sensor).where(Sensor.id == sensor_id))
    obj = res.one_or_none()

    if not obj:
        raise HTTPException(
            status_code=404, detail=f"ID: {sensor_id} not found"
        )

    update_data = sensor_update.model_dump(exclude_unset=True)
    obj.sqlmodel_update(update_data)

    session.add(obj)
    await session.commit()
    await session.refresh(obj)

    return obj


@router.delete("/{sensor_id}")
async def delete_sensor(
    sensor_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete a sensor by id"""
    res = await session.exec(select(Sensor).where(Sensor.id == sensor_id))

    obj = res.one_or_none()

    await session.delete(obj)
    await session.commit()

    return {"ok": True}
