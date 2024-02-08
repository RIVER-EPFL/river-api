from fastapi import Depends, APIRouter, Query, Response, HTTPException, Body
from sqlmodel import select
from app.db import get_session, AsyncSession
from app.utils import decode_base64
from app.stations.models import (
    Station,
    StationRead,
    StationUpdate,
    StationCreate,
    StationReadWithDataSummary,
    StationReadWithDataSummaryAndPlot,
    SensorDataSummary,
    SensorData,
    SensorDataRead,
)
from uuid import UUID
from sqlalchemy import func
import json
import csv

router = APIRouter()


# @router.get("/data/{stationdata_id}", response_model=SensorDataRead)
# async def get_stationdata(
#     session: AsyncSession = Depends(get_session),
#     *,
#     stationdata_id: UUID,
# ) -> SensorDataRead:
#     """Get an stationdata by id"""
#     res = await session.execute(
#         select(SensorData).where(SensorData.id == stationdata_id)
#     )
#     stationdata = res.scalars().one_or_none()

#     return stationdata


# @router.get("/data", response_model=list[SensorDataRead])
# async def get_all_stationdata(
#     response: Response,
#     session: AsyncSession = Depends(get_session),
#     *,
#     filter: str = Query(None),
#     sort: str = Query(None),
#     range: str = Query(None),
# ):
#     """Get all stationdatas"""
#     sort = json.loads(sort) if sort else []
#     range = json.loads(range) if range else []
#     filter = json.loads(filter) if filter else {}

#     # Do a query to satisfy total count for "Content-Range" header
#     count_query = select(func.count(SensorData.iterator))
#     if len(filter):
#         for field, value in filter.items():
#             if field == "id" or field == "station_id":
#                 count_query = count_query.filter(
#                     getattr(SensorData, field) == value
#                 )
#             else:
#                 count_query = count_query.filter(
#                     getattr(SensorData, field).like(f"%{str(value)}%")
#                 )
#     total_count = await session.execute(count_query)
#     total_count = total_count.scalar_one()

#     query = select(SensorData)

#     # Order by sort field params ie. ["name","ASC"]
#     if len(sort) == 2:
#         sort_field, sort_order = sort
#         if sort_order == "ASC":
#             query = query.order_by(getattr(SensorData, sort_field))
#         else:
#             query = query.order_by(getattr(SensorData, sort_field).desc())

#     # Filter by filter field params ie. {"name":"bar"}
#     if len(filter):
#         for field, value in filter.items():
#             if field == "id" or field == "station_id":
#                 query = query.filter(getattr(SensorData, field) == value)
#             else:
#                 query = query.filter(
#                     getattr(SensorData, field).like(f"%{str(value)}%")
#                 )

#     if len(range) == 2:
#         start, end = range
#         query = query.offset(start).limit(end - start + 1)
#     else:
#         start, end = [0, total_count]

#     # Execute query
#     results = await session.execute(query)
#     stationdatas = results.scalars().all()

#     response.headers["Content-Range"] = (
#         f"stationdatas {start}-{end}/{total_count}"
#     )

#     return stationdatas


# @router.post("/data", response_model=SensorDataRead)
# async def create_stationdata(
#     stationdata: SensorDataRead = Body(...),
#     session: AsyncSession = Depends(get_session),
# ) -> SensorDataRead:
#     """Creates an record of station data"""

#     stationdata = SensorData.from_orm(stationdata)
#     session.add(stationdata)
#     await session.commit()
#     await session.refresh(stationdata)

#     return stationdata


# @router.put("/data/{stationdata_id}", response_model=SensorDataRead)
# async def update_stationdata(
#     stationdata_id: UUID,
#     stationdata_update: SensorDataRead,
#     session: AsyncSession = Depends(get_session),
# ) -> SensorDataRead:
#     res = await session.execute(
#         select(SensorData).where(SensorData.id == stationdata_id)
#     )
#     stationdata_db = res.scalars().one()
#     stationdata_data = stationdata_update.dict(exclude_unset=True)
#     if not stationdata_db:
#         raise HTTPException(status_code=404, detail="SensorData not found")

#     # Update the fields from the request
#     for field, value in stationdata_data.items():
#         if field in ["latitude", "longitude"]:
#             # Don't process lat/lon, it's converted to geom in model validator
#             continue

#         print(f"Updating: {field}, {value}")
#         setattr(stationdata_db, field, value)

#     session.add(stationdata_db)
#     await session.commit()
#     await session.refresh(stationdata_db)

#     return stationdata_db


# @router.delete("/data/{stationdata_id}")
# async def delete_stationdata(
#     stationdata_id: UUID,
#     session: AsyncSession = Depends(get_session),
#     filter: dict[str, str] | None = None,
# ) -> None:
#     """Delete an stationdata by id"""
#     res = await session.execute(
#         select(SensorData).where(SensorData.id == stationdata_id)
#     )
#     stationdata = res.scalars().one_or_none()

#     if stationdata:
#         await session.delete(stationdata)
#         await session.commit()


@router.get("/{station_id}", response_model=StationReadWithDataSummaryAndPlot)
async def get_station(
    session: AsyncSession = Depends(get_session),
    *,
    station_id: UUID,
) -> StationRead:
    """Get an station by id"""

    query = (
        select(
            Station,
            func.count(SensorData.id).label("qty_records"),
            func.min(SensorData.time).label("start_date"),
            func.max(SensorData.time).label("end_date"),
        )
        .where(Station.id == station_id)
        .outerjoin(SensorData, Station.id == SensorData.station_id)
        .group_by(
            Station.id,
            Station.geom,
            Station.name,
            Station.description,
            Station.iterator,
        )
    )
    res = await session.execute(query)
    station = res.one_or_none()
    station_dict = station[0].dict() if station else {}

    # Do a query on the station data, at the moment this is raw, but should
    # probably be aggregated by day
    query = select(SensorData).where(SensorData.station_id == station_id)
    res = await session.execute(query)
    station_data = res.scalars().all()

    return StationReadWithDataSummaryAndPlot(
        **station_dict,
        data=SensorDataSummary(
            qty_records=station[1] if station else None,
            start_date=station[2] if station else None,
            end_date=station[3] if station else None,
        ),
        temperature_plot=station_data,
    )


@router.get("", response_model=list[StationReadWithDataSummary])
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
            if field == "id" or field == "area_id":
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
    query = (
        select(
            Station,
            func.count(SensorData.id).label("qty_records"),
            func.min(SensorData.time).label("start_date"),
            func.max(SensorData.time).label("end_date"),
        )
        .outerjoin(SensorData, Station.id == SensorData.station_id)
        .group_by(
            Station.id,
            Station.geom,
            Station.name,
            Station.description,
            Station.iterator,
        )
    )

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
            if field == "id" or field == "area_id":
                query = query.filter(getattr(Station, field) == value)
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
    stations = results.all()
    # print(stations)

    response.headers["Content-Range"] = f"stations {start}-{end}/{total_count}"

    # Add the summary information for the data (instead of the full data)
    stations_with_data = []
    for row in stations:
        stations_with_data.append(
            StationReadWithDataSummary(
                **row[0].dict(),
                data=SensorDataSummary(
                    qty_records=row[1],
                    start_date=row[2],
                    end_date=row[3],
                ),
            )
        )

    return stations_with_data


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
        if field in ["latitude", "longitude"]:
            # Don't process lat/lon, it's converted to geom in model validator
            continue
        if field == "instrumentdata":
            # Convert base64 to bytes, input should be csv, read and add rows
            # to station_data table with station_id
            rawdata, dtype = decode_base64(value)

            if dtype != "csv":
                raise HTTPException(
                    status_code=400,
                    detail="Only CSV files are supported",
                )
            # Treat the rawdata as a CSV file, read in the rows
            decoded = []
            for row in csv.reader(rawdata.decode("utf-8").splitlines()):
                decoded.append(row)

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
