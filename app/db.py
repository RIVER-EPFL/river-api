from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import config
from typing import AsyncGenerator, Any
from sqlmodel import select, update
from sqlalchemy.sql import func
from fastapi import Depends, Query
import json

engine = create_async_engine(
    config.DB_URL,
    echo=True,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_nested_model_field_names(
    schema: dict,
) -> list[str]:
    """Returns a list of field names that are nested models"""

    nested_model_field_names = []
    if "$defs" in schema:
        for field_name, properties in schema.get("properties", {}).items():
            if "items" in properties:
                ref = properties["items"].get("$ref")
                if ref and "#/$defs/" in ref:
                    nested_model_field_names.append(field_name)
    return nested_model_field_names


async def get_exact_match_fields(
    db_model,
) -> list[str]:
    """Returns a list of all the UUID fields in the model

    These cannot be performed with a likeness query and must have an
    exact match.

    """
    schema = db_model.model_json_schema()

    uuid_properties = []
    for prop_name, prop_details in schema["properties"].items():
        prop_type = prop_details.get("type")
        if isinstance(prop_type, list) and "string" in prop_type:
            any_of_types = prop_details.get("anyOf")
            if any_of_types:
                for any_of_type in any_of_types:
                    if "string" in any_of_type.get("type", []):
                        uuid_properties.append(prop_name)
                        break
            elif "format" in prop_details and prop_details["format"] == "uuid":
                uuid_properties.append(prop_name)
        elif prop_type in ["string", "null"]:  # Allow case when optional
            if "format" in prop_details and prop_details["format"] == "uuid":
                uuid_properties.append(prop_name)

    return uuid_properties


async def get_count(
    model: Any,
    filter: str = Query(None),
    session: AsyncSession = Depends(get_session),
) -> int:
    """Returns the count of a model with a filter applied"""

    filter = json.loads(filter) if filter else {}

    count_query = select(func.count(model.iterator))
    exact_match_fields = await get_exact_match_fields(model)
    if len(filter):
        for field, value in filter.items():
            if field in exact_match_fields:
                if isinstance(value, list):
                    for v in value:
                        count_query = count_query.filter(
                            getattr(model, field) == v
                        )
                else:
                    count_query = count_query.filter(
                        getattr(model, field) == value
                    )

    count = await session.exec(count_query)
    return count.one()


async def get_model_data(
    session: AsyncSession,
    model: Any,
    filter: dict,
    sort: list,
    range: list,
) -> list:
    """Returns the data of a model with a filter applied

    Similar to the count query except returns the data instead of the count"""

    query = select(model)
    exact_match_fields = await get_exact_match_fields(model)

    if len(filter):
        for field, value in filter.items():
            if field in exact_match_fields:
                if isinstance(value, list):
                    for v in value:
                        query = query.filter(getattr(model, field) == v)
                else:
                    query = query.filter(getattr(model, field) == value)

    if len(sort) == 2:
        sort_field, sort_order = sort
        if sort_order == "ASC":
            query = query.order_by(getattr(model, sort_field))
        else:
            query = query.order_by(getattr(model, sort_field).desc())

    if len(range):
        start, end = range
        query = query.offset(start).limit(end - start)

    res = await session.exec(query)

    return res.all()
