from pydantic import root_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class Config(BaseSettings):
    API_V1_PREFIX: str = "/v1"

    # Sensor settings
    DEFAULT_SENSOR_OUTPUT_RANGE: int = 4096

    # PostGIS settings
    DB_HOST: str | None
    DB_PORT: int = 5432
    DB_USER: str | None
    DB_PASSWORD: str | None

    DB_NAME: str = "postgres"
    DB_PREFIX: str = "postgresql+asyncpg"

    DB_URL: str | None = None

    # Astrocast API settings
    ASTROCAST_API_URL: str | None
    ASTROCAST_API_KEY: str | None
    ASTROCAST_POLLING_INTERVAL_SECONDS: int = 60
    ASTROCAST_RETRY_MIN_WAIT_SECONDS: int = 1
    ASTROCAST_RETRY_MAX_WAIT_SECONDS: int = 5

    @root_validator(pre=True)
    def form_db_url(cls, values: dict) -> dict:
        """Form the DB URL from the settings"""
        if "DB_URL" not in values:
            values["DB_URL"] = (
                "{prefix}://{user}:{password}@{host}:{port}/{db}".format(
                    prefix=values.get("DB_PREFIX"),
                    user=values.get("DB_USER"),
                    password=values.get("DB_PASSWORD"),
                    host=values.get("DB_HOST"),
                    port=values.get("DB_PORT"),
                    db=values.get("DB_NAME"),
                )
            )
        return values


class Constants(BaseSettings):
    # Sensor settings
    DEFAULT_SENSOR_OUTPUT_RANGE: int = 4096


@lru_cache()
def get_config():
    return Config()


@lru_cache()
def get_constants():
    return Constants()


constants = get_constants()
config = get_config()
