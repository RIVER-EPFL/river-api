from fastapi import Depends, APIRouter, Query, Response, Body, HTTPException
from sqlmodel import select
from app.db import get_session, AsyncSession
from app.sensor_devices.models import (
    SensorDeviceRead,
    SensorDevice,
    SensorDeviceCreate,
    SensorDeviceUpdate,
)
from uuid import UUID
from sqlalchemy import func
import json

router = APIRouter()


@router.get("/{device_id}", response_model=SensorDeviceRead)
async def get_device(
    session: AsyncSession = Depends(get_session),
    *,
    device_id: UUID,
) -> SensorDeviceRead:
    """Get an astrocast message by its local id"""

    res = await session.execute(
        select(SensorDevice).where(SensorDevice.id == device_id)
    )
    obj = res.scalars().one_or_none()

    return obj


@router.get("", response_model=list[SensorDeviceRead])
async def get_devices(
    response: Response,
    session: AsyncSession = Depends(get_session),
    *,
    filter: str = Query(None),
    sort: str = Query(None),
    range: str = Query(None),
) -> list[SensorDeviceRead]:
    """Get all astrocast messages"""

    sort = json.loads(sort) if sort else []
    range = json.loads(range) if range else []
    filter = json.loads(filter) if filter else {}

    # Do a query to satisfy total count for "Content-Range" header
    count_query = select(func.count(SensorDevice.iterator))
    if len(filter):  # Have to filter twice for some reason? SQLModel state?
        for field, value in filter.items():
            if field == "id":
                count_query = count_query.filter(
                    getattr(SensorDevice, field) == value
                )
            else:
                count_query = count_query.filter(
                    getattr(SensorDevice, field).like(f"%{str(value)}%")
                )
    total_count = await session.execute(count_query)
    total_count = total_count.scalar_one()

    # Query for the quantity of records in SensorInventoryData that match the
    # sensor as well as the min and max of the time column
    query = select(SensorDevice)

    # Order by sort field params ie. ["name","ASC"]
    if len(sort) == 2:
        sort_field, sort_order = sort
        if sort_order == "ASC":
            query = query.order_by(getattr(SensorDevice, sort_field))
        else:
            query = query.order_by(getattr(SensorDevice, sort_field).desc())

    # Filter by filter field params ie. {"name":"bar"}
    if len(filter):
        for field, value in filter.items():
            if field == "id":
                query = query.filter(getattr(SensorDevice, field) == value)
            else:
                query = query.filter(
                    getattr(SensorDevice, field).like(f"%{str(value)}%")
                )

    if len(range) == 2:
        start, end = range
        query = query.offset(start).limit(end - start + 1)
    else:
        start, end = [0, total_count]  # For content-range header

    # Execute query
    results = await session.execute(query)
    astrocast_messages = results.scalars().all()

    response.headers["Content-Range"] = (
        f"sensor_devices {start}-{end}/{total_count}"
    )

    return astrocast_messages


@router.post("", response_model=SensorDeviceRead)
async def create_device(
    device: SensorDeviceCreate = Body(...),
    session: AsyncSession = Depends(get_session),
) -> SensorDeviceRead:
    """Creates a device"""

    device = SensorDevice.from_orm(device)
    session.add(device)

    await session.commit()
    await session.refresh(device)

    return device


@router.put("/{device_id}", response_model=SensorDeviceRead)
async def update_device(
    device_id: UUID,
    device_update: SensorDeviceUpdate,
    session: AsyncSession = Depends(get_session),
) -> SensorDeviceRead:
    res = await session.execute(
        select(SensorDevice).where(SensorDevice.id == device_id)
    )
    device_db = res.scalars().one()
    device_data = device_update.dict(exclude_unset=True)
    if not device_db:
        raise HTTPException(status_code=404, detail="Device not found")

    # Update the fields from the request
    for field, value in device_data.items():
        print(f"Updating: {field}, {value}")
        setattr(device_db, field, value)

    session.add(device_db)
    await session.commit()
    await session.refresh(device_db)

    return device_db


@router.delete("/{device_id}")
async def delete_device(
    device_id: UUID,
    session: AsyncSession = Depends(get_session),
    filter: dict[str, str] | None = None,
) -> None:
    """Delete an device by id"""

    res = await session.execute(
        select(SensorDevice).where(SensorDevice.id == device_id)
    )
    device = res.scalars().one_or_none()

    if device:
        await session.delete(device)
        await session.commit()
