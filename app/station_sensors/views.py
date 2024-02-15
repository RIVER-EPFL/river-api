from fastapi import Depends, APIRouter, Query, Response, Body, HTTPException
from sqlmodel import select
from app.db import get_session, AsyncSession
from app.station_sensors.models import (
    StationSensorAssignmentsRead,
    StationSensorAssignments,
    StationSensorAssignmentsCreate,
    StationSensorAssignmentsUpdate,
)
from uuid import UUID
import json
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

router = APIRouter()


@router.get(
    "/{station_id}/{sensor_position}",
    response_model=StationSensorAssignmentsRead,
)
async def get_station_sensor_by_position(
    session: AsyncSession = Depends(get_session),
    *,
    station_id: UUID,
    sensor_position: int,
) -> StationSensorAssignmentsRead:
    """Get a station sensor relation by its local id"""

    if sensor_position < 1 or sensor_position > 15:
        raise HTTPException(
            status_code=400,
            detail="Invalid sensor position, must be between 1 and 15",
        )

    res = await session.exec(
        select(StationSensorAssignments)
        .where(StationSensorAssignments.station_id == station_id)
        .where(StationSensorAssignments.sensor_position == sensor_position)
    )
    obj = res.one_or_none()

    return obj


@router.get(
    "/{station_sensor_id}",
    response_model=StationSensorAssignmentsRead,
)
async def get_station_sensor(
    session: AsyncSession = Depends(get_session),
    *,
    station_sensor_id: UUID,
) -> StationSensorAssignmentsRead:
    """Get a station sensor relation by its local id"""

    res = await session.exec(
        select(StationSensorAssignments).where(
            StationSensorAssignments.id == station_sensor_id
        )
    )
    obj = res.one_or_none()

    return obj


@router.get("", response_model=list[StationSensorAssignmentsRead])
async def get_station_sensors(
    response: Response,
    session: AsyncSession = Depends(get_session),
    *,
    filter: str = Query(None),
    sort: str = Query(None),
    range: str = Query(None),
) -> list[StationSensorAssignmentsRead]:
    """Get all sensors"""

    sort = json.loads(sort) if sort else []
    range = json.loads(range) if range else []
    filter = json.loads(filter) if filter else {}

    # Do a query to satisfy total count for "Content-Range" header
    count_query = select(func.count(StationSensorAssignments.iterator))
    if len(filter):  # Have to filter twice for some reason? SQLModel state?
        for field, value in filter.items():
            if field == "id" or field == "station_id" or field == "sensor_id":
                if isinstance(value, list):
                    for v in value:
                        count_query = count_query.filter(
                            getattr(StationSensorAssignments, field) == v
                        )
                else:
                    count_query = count_query.filter(
                        getattr(StationSensorAssignments, field) == value
                    )
            else:
                count_query = count_query.filter(
                    getattr(StationSensorAssignments, field).like(
                        f"%{str(value)}%"
                    )
                )
    total_count = await session.exec(count_query)
    total_count = total_count.one()

    # Query for the quantity of records in SensorInventoryData that match the
    # sensor as well as the min and max of the time column
    query = select(StationSensorAssignments)

    # Order by sort field params ie. ["name","ASC"]
    if len(sort) == 2:
        sort_field, sort_order = sort
        if sort_order == "ASC":
            query = query.order_by(
                getattr(StationSensorAssignments, sort_field)
            )
        else:
            query = query.order_by(
                getattr(StationSensorAssignments, sort_field).desc()
            )

    # Filter by filter field params ie. {"name":"bar"}
    if len(filter):
        for field, value in filter.items():
            if field == "id" or field == "station_id" or field == "sensor_id":
                if isinstance(value, list):
                    for v in value:
                        count_query = count_query.filter(
                            getattr(StationSensorAssignments, field) == v
                        )
                else:
                    count_query = count_query.filter(
                        getattr(StationSensorAssignments, field) == value
                    )
            else:
                query = query.filter(
                    getattr(StationSensorAssignments, field).like(
                        f"%{str(value)}%"
                    )
                )

    if len(range) == 2:
        start, end = range
        query = query.offset(start).limit(end - start + 1)
    else:
        start, end = [0, total_count]  # For content-range header

    # Execute query
    results = await session.exec(query)
    station_sensors = results.all()

    response.headers["Content-Range"] = (
        f"station_sensors {start}-{end}/{total_count}"
    )

    return station_sensors


@router.post("", response_model=StationSensorAssignmentsRead)
async def create_station_sensor_mapping(
    station_sensor: StationSensorAssignmentsCreate = Body(...),
    session: AsyncSession = Depends(get_session),
) -> StationSensorAssignmentsRead:
    """Creates a station-sensor mapping"""

    obj = StationSensorAssignments.model_validate(station_sensor)
    try:
        session.add(obj)

        await session.commit()
    except IntegrityError as e:
        # Catch integrity error
        # except Exception as e:

        await session.rollback()

        if "sensor_position_constraint" in str(e.orig):
            raise HTTPException(
                status_code=409,
                detail=f"Position {obj.sensor_position} already assigned to a "
                f"sensor on station {obj.station_id}",
            )
        else:
            raise HTTPException(
                status_code=409,
                detail="Integrity error, likely a duplicate entry",
            )
    await session.refresh(obj)

    return obj


@router.put(
    "/{station_sensor_id}",
    response_model=StationSensorAssignmentsRead,
)
async def update_sensor(
    station_sensor_id: UUID,
    station_sensor_update: StationSensorAssignmentsUpdate,
    session: AsyncSession = Depends(get_session),
) -> StationSensorAssignmentsRead:
    """Update the mapping of a sensor to a station by id and position"""

    res = await session.exec(
        select(StationSensorAssignments).where(
            StationSensorAssignments.id == station_sensor_id
        )
    )
    station_sensor_db = res.one_or_none()
    if not station_sensor_db:
        raise HTTPException(status_code=404, detail="Station-Sensor not found")

    station_sensor_data = station_sensor_update.model_dump(exclude_unset=True)

    # Update the fields from the request
    for field, value in station_sensor_data.items():
        print(f"Updating: {field}, {value}")
        setattr(station_sensor_db, field, value)

    session.add(station_sensor_db)
    await session.commit()
    await session.refresh(station_sensor_db)

    return station_sensor_db


@router.delete(
    "/{station_sensor_id}",
)
async def delete_station_sensor_mapping(
    station_sensor_id: UUID,
    session: AsyncSession = Depends(get_session),
    filter: dict[str, str] | None = None,
) -> None:
    """Remove a sensor from a station by id and position"""

    res = await session.exec(
        select(StationSensorAssignments).where(
            StationSensorAssignments.id == station_sensor_id
        )
    )
    station_sensor = res.one_or_none()

    if station_sensor:
        await session.delete(station_sensor)
        await session.commit()
