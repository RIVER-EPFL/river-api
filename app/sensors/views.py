from fastapi import Depends, APIRouter, Query, Response, Body, HTTPException
from sqlmodel import select
from app.db import get_session, AsyncSession
from app.sensors.models import (
    SensorRead,
    Sensor,
    SensorCreate,
    SensorUpdate,
    SensorCalibration,
)
from uuid import UUID
from sqlalchemy import func, not_
import json
from typing import Any
from app.db import async_session
from sqlmodel_react_admin.routers import ReactAdminRouter

# router = APIRouter()

# from app.db import engine


router = ReactAdminRouter(
    db_model=Sensor,
    create_model=SensorCreate,
    read_model=SensorRead,
    update_model=SensorUpdate,
    name_singular="sensor",
    prefix="/sensors",
    db_sessionmaker=async_session,
)


# @router.get("/{sensor_id}", response_model=SensorRead)
# async def get_sensor(
#     session: AsyncSession = Depends(get_session),
#     *,
#     sensor_id: UUID,
# ) -> SensorRead:
#     """Get a sensor by its local id"""

#     res = await session.exec(select(Sensor).where(Sensor.id == sensor_id))
#     obj = res.one_or_none()

#     return obj


# @router.get("", response_model=list[SensorRead])
# async def get_sensors(
#     response: Response,
#     session: AsyncSession = Depends(get_session),
#     *,
#     filter: str = Query(None),
#     sort: str = Query(None),
#     range: str = Query(None),
# ) -> list[SensorRead]:
#     """Get all sensors

#     Filter query on station_link as true false returns results with a station
#     link or not.
#     """

#     sort = json.loads(sort) if sort else []
#     range = json.loads(range) if range else []
#     filter = json.loads(filter) if filter else {}

#     # Do a query to satisfy total count for "Content-Range" header
#     count_query = select(func.count(Sensor.iterator))
#     if len(filter):  # Have to filter twice for some reason? SQLModel state?
#         for field, value in filter.items():
#             if field == "id":
#                 if isinstance(value, list):
#                     for v in value:
#                         count_query = count_query.filter(
#                             getattr(Sensor, field) == v
#                         )
#                 else:
#                     count_query = count_query.filter(
#                         getattr(Sensor, field) == value
#                     )
#             elif field == "station_link":
#                 # Boolean query on if there's a station link (true)/not (false)
#                 if value:  # Query on if there's a station link
#                     count_query = count_query.filter(Sensor.station_link.has())
#                 else:
#                     count_query = count_query.filter(  # No station link
#                         not_(Sensor.station_link.has())
#                     )
#             else:
#                 count_query = count_query.filter(
#                     getattr(Sensor, field).like(f"%{str(value)}%")
#                 )
#     total_count = await session.exec(count_query)
#     total_count = total_count.one()

#     # Query for the quantity of records in SensorInventoryData that match the
#     # sensor as well as the min and max of the time column
#     query = select(Sensor)

#     # Order by sort field params ie. ["name","ASC"]
#     if len(sort) == 2:
#         sort_field, sort_order = sort
#         if sort_order == "ASC":
#             query = query.order_by(getattr(Sensor, sort_field))
#         else:
#             query = query.order_by(getattr(Sensor, sort_field).desc())

#     # Filter by filter field params ie. {"name":"bar"}
#     if len(filter):
#         for field, value in filter.items():
#             if field == "id":
#                 if isinstance(value, list):
#                     for v in value:
#                         count_query = count_query.filter(
#                             getattr(Sensor, field) == v
#                         )
#                 else:
#                     count_query = count_query.filter(
#                         getattr(Sensor, field) == value
#                     )
#             elif field == "station_link":
#                 # Boolean query on if there's a station link (true)/not (false)
#                 if value:
#                     query = query.filter(Sensor.station_link.has())
#                 else:
#                     query = query.filter(not_(Sensor.station_link.has()))
#             else:
#                 query = query.filter(
#                     getattr(Sensor, field).like(f"%{str(value)}%")
#                 )

#     if len(range) == 2:
#         start, end = range
#         query = query.offset(start).limit(end - start + 1)
#     else:
#         start, end = [0, total_count]  # For content-range header

#     # Execute query
#     results = await session.exec(query)
#     astrocast_messages = results.all()

#     response.headers["Content-Range"] = f"sensors {start}-{end}/{total_count}"

#     return astrocast_messages


# @router.post("", response_model=SensorRead)
# async def create_sensor(
#     sensor: SensorCreate = Body(...),
#     session: AsyncSession = Depends(get_session),
# ) -> SensorRead:
#     """Creates a device"""

#     sensor = Sensor.model_validate(sensor)
#     session.add(sensor)

#     await session.commit()
#     await session.refresh(sensor)

#     return sensor


# @router.put("/{sensor_id}", response_model=SensorRead)
# async def update_sensor(
#     sensor_id: UUID,
#     sensor_update: SensorUpdate,
#     session: AsyncSession = Depends(get_session),
# ) -> SensorRead:
#     res = await session.exec(select(Sensor).where(Sensor.id == sensor_id))
#     sensor_db = res.one()
#     sensor_data = sensor_update.model_dump(exclude_unset=True)
#     if not sensor_db:
#         raise HTTPException(status_code=404, detail="Device not found")

#     # We should replace the
#     sensor_calibrations = []
#     # Update the fields from the request
#     for field, value in sensor_data.items():
#         if field == "calibrations":
#             # First delete all the calibrations if there are any
#             if sensor_db.calibrations:

#                 for db_obj in sensor_db.calibrations:
#                     print(db_obj)
#                     await session.delete(db_obj)

#             # Update the calibrations
#             for calibration in value:
#                 print(calibration)
#                 obj = SensorCalibration.model_validate(calibration)
#                 sensor_db.calibrations.append(obj)
#                 # session.add(obj)
#                 # sensor_db.calibrations.append(obj)
#             setattr(sensor_db.calibrations, field, sensor_calibrations)
#         else:
#             setattr(sensor_db, field, value)

#     session.add(sensor_db)
#     await session.commit()
#     await session.refresh(sensor_db)

#     return sensor_db


# @router.delete("/{sensor_id}")
# async def delete_device(
#     sensor_id: UUID,
#     session: AsyncSession = Depends(get_session),
#     filter: dict[str, str] | None = None,
# ) -> None:
#     """Delete an device by id"""

#     res = await session.exec(select(Sensor).where(Sensor.id == sensor_id))
#     sensor = res.one_or_none()

#     if sensor:
#         await session.delete(sensor)
#         await session.commit()
