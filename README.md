# RIVER API
The backend API for the RIVER lab.


## Application relationships

This API supports the following applications:

- [astroriver-bff](https://github.com/RIVER-EPFL/astroriver-bff)
- [astroriver-ui](https://github.com/RIVER-EPFL/astroriver-ui)

## Getting started

### Environment variables

The following environment variables are required to run the API:

# Postrges settings
- `DB_HOST`: the hostname of the database server
- `DB_PORT`: the port of the database server
- `DB_USER`: the username to connect to the database
- `DB_PASSWORD`: the password to connect to the database

# Astrocast API settings. Get token from https://api.astrocast.com
- `ASTROCAST_API_URL`: the URL of the Astrocast API
- `ASTROCAST_API_KEY`: the API key for the Astrocast API



### Seed the database with some data

Assuming the credentials for the database are `postgres:psql@localhost:5433/postgres` and the database is empty, run the following command to seed the database with some data:

`poetry run python seed_db.py postgresql+asyncpg://postgres:psql@localhost:5433/postgres`

### Run the server
Build the docker image:

`docker build -t river-api .`

Run a PostGIS server, then run the docker image:
```
docker run \
    -e DB_HOST=<postgis hostname>
    -e DB_PORT=<postgis port>
    -e DB_USER=<postgis user>
    -e DB_PASSWORD=<postgis password>
    -e DB_NAME=<postgis dbname>
    -e DB_PREFIX=postgresql+asyncpg
    docker.io/library/river-api:latest
```

The [astroriver-ui repository](https://github.com/LabRIVER/astroriver-ui) has a development docker-compose.yaml file to load the API, BFF, PostGIS and UI all together, assuming all repositories are cloned locally.