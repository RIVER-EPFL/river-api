from pydantic import BaseSettings, root_validator
from functools import lru_cache


class Config(BaseSettings):
    API_V1_PREFIX = "/v1"

    # PostGIS settings
    DB_HOST: str
    DB_PORT: int  # 5432
    DB_USER: str
    DB_PASSWORD: str

    DB_NAME: str = "postgres"
    DB_PREFIX: str = "postgresql+asyncpg"

    DB_URL: str | None = None

    # Astrocast API settings
    ASTROCAST_API_URL: str
    ASTROCAST_API_KEY: str
    ASTROCAST_POLLING_INTERVAL_SECONDS: int = 60
    ASTROCAST_RETRY_MIN_WAIT_SECONDS: int = 1
    ASTROCAST_RETRY_MAX_WAIT_SECONDS: int = 5

    @root_validator(pre=True)
    def form_db_url(cls, values: dict) -> dict:
        """Form the DB URL from the settings"""
        if "DB_URL" not in values:
            values[
                "DB_URL"
            ] = "{prefix}://{user}:{password}@{host}:{port}/{db}".format(
                prefix=values["DB_PREFIX"],
                user=values["DB_USER"],
                password=values["DB_PASSWORD"],
                host=values["DB_HOST"],
                port=values["DB_PORT"],
                db=values["DB_NAME"],
            )
        return values


@lru_cache()
def get_config():
    return Config()


config = get_config()
