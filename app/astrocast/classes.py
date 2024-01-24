import aiohttp
from app.config import config
from fastapi import Depends
from app.astrocast.models import AstrocaseMessageCreate, AstrocastMessage
import tenacity
import base64
from sqlmodel import select
import asyncio
import datetime
from app.db import async_session
from sqlmodel.ext.asyncio.session import AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker


class AstrocastAPI:
    def __init__(
        self,
        api_token: str = config.ASTROCAST_API_KEY,
        api_url: str = config.ASTROCAST_API_URL,
    ) -> None:
        self.api_token: str = api_token
        self.api_url: str = api_url
        self.poll_messages: bool = True
        self.last_polling_time: datetime.datetime | None = None

    @tenacity.retry(
        wait=tenacity.wait_random(
            min=config.ASTROCAST_RETRY_MIN_WAIT_SECONDS,
            max=config.ASTROCAST_RETRY_MAX_WAIT_SECONDS,
        ),
        reraise=True,
    )
    async def get_messages(
        self,
        only_new_messages: bool = True,
    ):
        """Get the latest messages from the Astrocast API

        Parameters
        ----------
        only_new_messages : bool, optional
            Only get messages that have not been previously retrieved,
            by default True. This uses the `get_time_of_last_saved_message()`
            to determine the last time a message was retrieved from the API.
        """

        # Set the last polling time in the state of the class
        self.last_polling_time = datetime.datetime.utcnow()

        print(f"Getting messages ({self.last_polling_time})...")

        # Get the last retrieved message time that we saved locally
        if only_new_messages:
            last_db_message_time = await self.get_time_of_last_saved_message()
            if last_db_message_time:
                formed_api_url = (
                    f"{self.api_url}/messages?startReceivedDate="
                    f'{last_db_message_time.strftime("%Y-%m-%dT%H:%M:%S")}Z'
                )
            else:
                formed_api_url = f"{self.api_url}/messages"
        else:
            formed_api_url = f"{self.api_url}/messages"

        async with aiohttp.ClientSession() as session:
            async with session.get(
                formed_api_url,
                headers={"X-Api-Key": str(self.api_token)},
            ) as response:
                if response.status == 200:
                    messages = await response.json()
                    if len(messages) > 0:
                        print(f"Got {len(messages)} messages.")

                        # Compile message into objects
                        for message in messages:
                            await self.add_message_to_db(message)
                    else:
                        print("There is no message.")
                else:
                    print("Error, something is wrong in the request.")

        return

    async def add_message_to_db(
        self,
        message: dict,
    ) -> None:
        """Add a message to the database"""
        payload = AstrocaseMessageCreate(
            requested_at=self.last_polling_time,
            messageGuid=message["messageGuid"],
            deviceGuid=message["deviceGuid"],
            createdDate=message["createdDate"],
            receivedDate=message["receivedDate"],
            latitude=message["latitude"],
            longitude=message["longitude"],
            data=message["data"],
            messageSize=message["messageSize"],
            callbackDeliveryStatus=message["callbackDeliveryStatus"],
        )
        import sqlalchemy

        try:
            async with async_session() as db_session:
                obj_astrocast = AstrocastMessage.from_orm(payload)
                db_session.add(obj_astrocast)
                await db_session.commit()
        except sqlalchemy.exc.IntegrityError:
            print(
                f'Duplicate messageGuid ({message["messageGuid"]}), skipping...',
            )

    async def get_time_of_last_saved_message(
        self,
    ) -> datetime.datetime | None:
        """Get the time of the last message to minimise API queries

        Time is based off of the receivedDate field in the Astrocast API spec.
        """
        async with async_session() as db_session:
            query = select(AstrocastMessage).order_by(
                AstrocastMessage.receivedDate.desc(),
            )
            results = await db_session.execute(query)
            last_message = results.scalars().first()
            if last_message:
                return last_message.receivedDate
            else:
                return None

    async def start_collecting_messages(
        self,
        interval_seconds: int = config.ASTROCAST_POLLING_INTERVAL_SECONDS,
    ) -> None:
        """Poll the Astrocast API for new messages"""
        # Poll the Astrocast API for new messages

        while self.poll_messages:
            last_db_message_time = await self.get_time_of_last_saved_message()
            print(f"Last message retrieved at: {last_db_message_time}")
            await self.get_messages()  # Get the latest messages
            await asyncio.sleep(interval_seconds)  # Wait before polling again

    @property
    def is_polling_messages(
        self,
    ) -> bool:
        """Check if the Astrocast API is currently polling for messages"""
        return self.poll_messages

    @property
    def last_message_polling_time(
        self,
    ) -> datetime.datetime | None:
        """Get the last time the Astrocast API polled for messages"""
        return self.last_polling_time

    @property
    def next_message_polling_time(
        self,
    ) -> datetime.datetime | None:
        """Get the next time the Astrocast API will poll for messages"""
        if self.last_polling_time:
            return self.last_polling_time + datetime.timedelta(
                seconds=config.ASTROCAST_POLLING_INTERVAL_SECONDS
            )
        else:
            return None


def get_astrocast_api():
    return AstrocastAPI()


astrocast_api = get_astrocast_api()
