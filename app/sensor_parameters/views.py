from app.sensor_parameters.models import (
    SensorParameter,
    SensorParameterCreate,
    SensorParameterRead,
    SensorParameterUpdate,
)

from app.db import get_session, AsyncSession
from fastapi import Depends, APIRouter, Query, Response, HTTPException
from sqlmodel import select
from uuid import UUID
from typing import Any
import json
from app.crud import CRUD

router = APIRouter()
crud = CRUD(
    SensorParameter,
    SensorParameterRead,
    SensorParameterCreate,
    SensorParameterUpdate,
)


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


@router.get("/{sensorparameter_id}", response_model=SensorParameterRead)
async def get_sensor_parameter(
    session: AsyncSession = Depends(get_session),
    *,
    sensorparameter_id: UUID,
) -> SensorParameterRead:
    """Get an sensorparameter by id"""

    res = await session.exec(
        select(SensorParameter).where(SensorParameter.id == sensorparameter_id)
    )

    obj = res.one_or_none()

    return obj


@router.get("", response_model=list[SensorParameterRead])
async def get_all_sensor_parameter(
    response: Response,
    objs: CRUD = Depends(get_data),
    total_count: int = Depends(get_count),
) -> list[SensorParameterRead]:
    """Get all sensor parameter"""

    return objs


@router.post("", response_model=SensorParameterRead)
async def create_sensorparameter(
    sensorparameter: SensorParameterCreate,
    session: AsyncSession = Depends(get_session),
) -> SensorParameterRead:
    """Creates a sensor parameter record"""

    obj = SensorParameter.model_validate(sensorparameter)

    session.add(obj)
    await session.commit()
    await session.refresh(obj)

    return obj


@router.put("/{sensorparameter_id}", response_model=Any)
async def update_sensorparameter(
    sensorparameter_id: UUID,
    sensorparameter_update: SensorParameterUpdate,
    session: AsyncSession = Depends(get_session),
) -> SensorParameterRead:
    """Update an sensorparameter by id"""

    res = await session.exec(
        select(SensorParameter).where(SensorParameter.id == sensorparameter_id)
    )
    obj = res.one_or_none()

    if not obj:
        raise HTTPException(
            status_code=404, detail=f"ID: {sensorparameter_id} not found"
        )

    update_data = sensorparameter_update.model_dump(exclude_unset=True)
    obj.sqlmodel_update(update_data)

    session.add(obj)
    await session.commit()
    await session.refresh(obj)

    return obj


@router.delete("/{sensorparameter_id}")
async def delete_sensorparameter(
    sensorparameter_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete an sensorparameter by id"""
    res = await session.exec(
        select(SensorParameter).where(SensorParameter.id == sensorparameter_id)
    )

    obj = res.one_or_none()

    await session.delete(obj)
    await session.commit()

    return {"ok": True}
