from fastapi import Depends, APIRouter, Query, Response, HTTPException, Body
from sqlmodel import select
from app.db import get_session, AsyncSession
from app.stations.models import (
    Station,
    StationRead,
    StationUpdate,
    StationCreate,
)
from app.station_sensors.models import StationSensorAssignments
from app.sensors.models import Sensor
from uuid import UUID
from sqlalchemy import func
import json

router = APIRouter()


@router.get("/{station_id}", response_model=StationRead)
async def get_station(
    session: AsyncSession = Depends(get_session),
    *,
    station_id: UUID,
) -> StationRead:
    """Get an station by id"""

    # Query for the station, joining the full sensor object where the
    # station.sensors is the link table
    query = select(Station).where(Station.id == station_id)
    res = await session.exec(query)

    station_data = res.one_or_none()

    return station_data


@router.get("", response_model=list[StationRead])
async def get_stations(
    response: Response,
    session: AsyncSession = Depends(get_session),
    *,
    filter: str = Query(None),
    sort: str = Query(None),
    range: str = Query(None),
):
    """Get all stations"""
    sort = json.loads(sort) if sort else []
    range = json.loads(range) if range else []
    filter = json.loads(filter) if filter else {}

    # Do a query to satisfy total count for "Content-Range" header
    count_query = select(func.count(Station.iterator))
    if len(filter):  # Have to filter twice for some reason? SQLModel state?
        for field, value in filter.items():
            if field == "id":
                if isinstance(value, list):
                    for v in value:
                        count_query = count_query.filter(
                            getattr(Station, field) == v
                        )
                else:
                    count_query = count_query.filter(
                        getattr(Station, field) == value
                    )
            else:
                count_query = count_query.filter(
                    getattr(Station, field).like(f"%{str(value)}%")
                )
    total_count = await session.execute(count_query)
    total_count = total_count.scalar_one()

    # Query for the quantity of records in SensorData matching the station as
    # well as the min and max of the time column
    query = select(Station)

    # Order by sort field params ie. ["name","ASC"]
    if len(sort) == 2:
        sort_field, sort_order = sort
        if sort_order == "ASC":
            query = query.order_by(getattr(Station, sort_field))
        else:
            query = query.order_by(getattr(Station, sort_field).desc())

    # Filter by filter field params ie. {"name":"bar"}
    if len(filter):
        for field, value in filter.items():
            if field == "id":
                if isinstance(value, list):
                    for v in value:
                        count_query = count_query.filter(
                            getattr(Station, field) == v
                        )
                else:
                    count_query = count_query.filter(
                        getattr(Station, field) == value
                    )
            else:
                query = query.filter(
                    getattr(Station, field).like(f"%{str(value)}%")
                )

    if len(range) == 2:
        start, end = range
        query = query.offset(start).limit(end - start + 1)
    else:
        start, end = [0, total_count]  # For content-range header

    # Execute query
    results = await session.execute(query)
    stations = results.scalars().all()

    response.headers["Content-Range"] = f"stations {start}-{end}/{total_count}"

    return stations


@router.post("", response_model=StationRead)
async def create_station(
    station: StationCreate = Body(...),
    session: AsyncSession = Depends(get_session),
) -> StationRead:
    """Creates a station"""

    station = Station.from_orm(station)
    session.add(station)

    await session.commit()
    await session.refresh(station)

    return station


@router.put("/{station_id}", response_model=StationRead)
async def update_station(
    station_id: UUID,
    station_update: StationUpdate,
    session: AsyncSession = Depends(get_session),
) -> StationRead:
    res = await session.execute(
        select(Station).where(Station.id == station_id)
    )
    station_db = res.scalars().one()
    station_data = station_update.dict(exclude_unset=True)
    if not station_db:
        raise HTTPException(status_code=404, detail="Station not found")

    # Update the fields from the request
    for field, value in station_data.items():
        print(f"Updating: {field}, {value}")
        setattr(station_db, field, value)

    session.add(station_db)
    await session.commit()
    await session.refresh(station_db)

    return station_db


@router.delete("/{station_id}")
async def delete_station(
    station_id: UUID,
    session: AsyncSession = Depends(get_session),
    filter: dict[str, str] | None = None,
) -> None:
    """Delete an station by id"""
    res = await session.execute(
        select(Station).where(Station.id == station_id)
    )
    station = res.scalars().one_or_none()

    if station:
        await session.delete(station)
        await session.commit()
