from fastapi import Depends, APIRouter, Query, Response, HTTPException, Body
from sqlmodel import select
from app.db import get_session, AsyncSession
from app.utils import decode_base64
from app.astrocast.models import AstrocastMessageRead, AstrocastMessage
from uuid import UUID
from sqlalchemy import func
import json

router = APIRouter()


## Astrocast data


@router.get("/{astrocast_id}", response_model=AstrocastMessageRead)
async def get_astrocast_message(
    session: AsyncSession = Depends(get_session),
    *,
    astrocast_id: UUID,
) -> AstrocastMessageRead:
    """Get an astrocast message by its local id"""

    res = await session.execute(
        select(AstrocastMessage).where(AstrocastMessage.id == astrocast_id)
    )
    obj = res.scalars().one_or_none()

    return obj


@router.get("", response_model=list[AstrocastMessageRead])
async def get_astrocast_messages(
    response: Response,
    session: AsyncSession = Depends(get_session),
    *,
    filter: str = Query(None),
    sort: str = Query(None),
    range: str = Query(None),
) -> list[AstrocastMessageRead]:
    """Get all astrocast messages"""
    sort = json.loads(sort) if sort else []
    range = json.loads(range) if range else []
    filter = json.loads(filter) if filter else {}

    # Do a query to satisfy total count for "Content-Range" header
    count_query = select(func.count(AstrocastMessage.iterator))
    if len(filter):  # Have to filter twice for some reason? SQLModel state?
        for field, value in filter.items():
            if field == "id" or field == "area_id":
                count_query = count_query.filter(
                    getattr(AstrocastMessage, field) == value
                )
            else:
                count_query = count_query.filter(
                    getattr(AstrocastMessage, field).like(f"%{str(value)}%")
                )
    total_count = await session.execute(count_query)
    total_count = total_count.scalar_one()

    # Query for the quantity of records in AstrocastMessageData that match the sensor as
    # well as the min and max of the time column
    query = select(AstrocastMessage)

    # Order by sort field params ie. ["name","ASC"]
    if len(sort) == 2:
        sort_field, sort_order = sort
        if sort_order == "ASC":
            query = query.order_by(getattr(AstrocastMessage, sort_field))
        else:
            query = query.order_by(
                getattr(AstrocastMessage, sort_field).desc()
            )

    # Filter by filter field params ie. {"name":"bar"}
    if len(filter):
        for field, value in filter.items():
            if field == "id" or field == "area_id":
                query = query.filter(getattr(AstrocastMessage, field) == value)
            else:
                query = query.filter(
                    getattr(AstrocastMessage, field).like(f"%{str(value)}%")
                )

    if len(range) == 2:
        start, end = range
        query = query.offset(start).limit(end - start + 1)
    else:
        start, end = [0, total_count]  # For content-range header

    # Execute query
    results = await session.execute(query)
    astrocast_messages = results.scalars().all()
    # print(astrocast_messages)

    response.headers[
        "Content-Range"
    ] = f"astrocast_messages {start}-{end}/{total_count}"

    return astrocast_messages
