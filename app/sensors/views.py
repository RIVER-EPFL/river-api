from app.sensors.models import (
    SensorRead,
    Sensor,
    SensorCreate,
    SensorUpdate,
)
from app.db import get_session, AsyncSession
from fastapi import Depends, APIRouter, Query, Response, HTTPException
from sqlmodel import select
from uuid import UUID
from typing import Any
from app.crud import CRUD
from app.utils import generate_random_id

router = APIRouter()
crud = CRUD(Sensor, SensorRead, SensorCreate, SensorUpdate)


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

    return res


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


@router.get("/{sensor_id}", response_model=SensorRead)
async def get_sensor(
    session: AsyncSession = Depends(get_session),
    *,
    sensor_id: UUID,
) -> SensorRead:
    """Get a sensor by id"""

    res = await session.exec(select(Sensor).where(Sensor.id == sensor_id))

    obj = res.one_or_none()

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

    print(f"FIELD_IDS: {existing_field_ids}")

    # Generate a random field_id
    field_id = generate_random_id()
    while field_id in existing_field_ids:
        field_id = generate_random_id()
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
