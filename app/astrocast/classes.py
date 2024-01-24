import aiohttp
from app.config import config
from app.astrocast.models import AstrocastMessage
import tenacity
import base64
import asyncio
import datetime


class AstrocastAPI:
    def __init__(
        self,
        api_token: str = config.ASTROCAST_API_KEY,
        api_url: str = config.ASTROCAST_API_URL,
    ) -> None:
        self.api_token: str = api_token
        self.api_url: str = api_url
        self.poll_messages: bool = True
        self.time_last_message_polling: datetime.datetime | None = None

    @tenacity.retry(
        wait=tenacity.wait_random(
            min=config.ASTROCAST_RETRY_MIN_WAIT_SECONDS,
            max=config.ASTROCAST_RETRY_MAX_WAIT_SECONDS,
        ),
        reraise=True,
    )
    async def get_messages(self):
        """Get the latest messages from the Astrocast API"""

        print("Getting messages...")
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/messages",
                headers={"X-Api-Key": str(self.api_token)},
            ) as response:
                if response.status == 200:
                    messages = await response.json()
                    if len(messages) > 0:
                        for message in messages:
                            payload = AstrocastMessage(
                                messageGuid=message["messageGuid"],
                                deviceGuid=message["deviceGuid"],
                                createdDate=message["createdDate"],
                                receivedDate=message["receivedDate"],
                                latitude=message["latitude"],
                                longitude=message["longitude"],
                                data=message["data"],
                                messageSize=message["messageSize"],
                                callbackDeliveryStatus=message[
                                    "callbackDeliveryStatus"
                                ],
                            )
                            print(payload)
                    else:
                        print("There is no message.")
                else:
                    print("Error, something is wrong in the request.")

        self.time_last_message_polling = datetime.datetime.utcnow()

        return

    async def start_collecting_messages(
        self,
        interval_seconds: int = config.ASTROCAST_POLLING_INTERVAL_SECONDS,
    ) -> None:
        """Poll the Astrocast API for new messages"""
        # Poll the Astrocast API for new messages

        while self.poll_messages:
            await self.get_messages()  # Get the latest messages
            await asyncio.sleep(interval_seconds)  # Wait before polling again

    @property
    def is_polling_messages(self) -> bool:
        """Check if the Astrocast API is currently polling for messages"""
        return self.poll_messages

    @property
    def last_message_polling_time(self) -> datetime.datetime | None:
        """Get the last time the Astrocast API polled for messages"""
        return self.time_last_message_polling

    @property
    def next_message_polling_time(self) -> datetime.datetime | None:
        """Get the next time the Astrocast API will poll for messages"""
        if self.time_last_message_polling:
            return self.time_last_message_polling + datetime.timedelta(
                seconds=config.ASTROCAST_POLLING_INTERVAL_SECONDS
            )
        else:
            return None


def get_astrocast_api():
    return AstrocastAPI()


astrocast_api = get_astrocast_api()
