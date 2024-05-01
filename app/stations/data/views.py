from app.stations.data.models import (
    StationData,
    StationDataRead,
    StationDataCreate,
    StationDataUpdate,
)
from app.db import get_session, AsyncSession
from fastapi import Depends, APIRouter, Query, Response, HTTPException
from sqlmodel import select
from uuid import UUID
from typing import Any
from app.crud import CRUD


router = APIRouter()
crud = CRUD(
    StationData,
    StationDataRead,
    StationDataCreate,
    StationDataUpdate,
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


@router.get("/{stationdata_id}", response_model=StationDataRead)
async def get_station_data(
    session: AsyncSession = Depends(get_session),
    *,
    stationdata_id: UUID,
) -> StationDataRead:
    """Get station data by id"""

    res = await session.exec(
        select(StationData).where(StationData.id == stationdata_id)
    )

    obj = res.one_or_none()

    return obj


@router.get("", response_model=list[StationDataRead])
async def get_all_station_data(
    response: Response,
    stations: CRUD = Depends(get_data),
    total_count: int = Depends(get_count),
) -> list[StationDataRead]:
    """Get all station data"""

    return stations


import time
import datetime
from app.stations.models import Station
from app.utils import (
    get_unix_time_from_str,
    extract_raw_values_from_str,
    parse_station_data,
    generate_random_id,
)


@router.post("", response_model=Any)
async def create_stationdata(
    stationdata: StationDataCreate,
    session: AsyncSession = Depends(get_session),
) -> StationDataRead:
    """Creates a station data record"""

    obj = await parse_station_data(stationdata, session)
    print(obj.recorded_at)

    # obj = StationData.model_validate(stationdata)

    # session.add(obj)
    # await session.commit()
    # await session.refresh(obj)

    return obj


@router.put("/{stationdata_id}", response_model=Any)
async def update_stationdata(
    stationdata_id: UUID,
    stationdata_update: StationDataUpdate,
    session: AsyncSession = Depends(get_session),
) -> StationDataRead:
    """Update station data by id"""

    res = await session.exec(
        select(StationData).where(StationData.id == stationdata_id)
    )
    obj = res.one_or_none()

    if not obj:
        raise HTTPException(
            status_code=404, detail=f"ID: {stationdata_id} not found"
        )

    update_data = stationdata_update.model_dump(exclude_unset=True)
    obj.sqlmodel_update(update_data)

    session.add(obj)
    await session.commit()
    await session.refresh(obj)

    return obj


@router.delete("/{stationdata_id}")
async def delete_stationdata(
    stationdata_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete station data by id"""
    res = await session.exec(
        select(StationData).where(StationData.id == stationdata_id)
    )

    obj = res.one_or_none()

    await session.delete(obj)
    await session.commit()

    return {"ok": True}
