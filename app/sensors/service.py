## Provides a collection service from the Astrocast API
# from app.config import config


import requests, base64
from datetime import datetime, timedelta
import aiohttp

apiToken = "BCkYymjpmSlIEIp0Y3BXOamPxl4ShDpi5bMArg8g1tFNkHtpzDyFh7jfF5LZN437hj4shleWXE7pJUNUnUJlNHma3GIbUWHF"
startReceivedDate = datetime.now() - timedelta(minutes=60)

response = requests.get(
    "https://api.astrocast.com/v1/messages/",
    # ?startReceivedDate="
    # + str(startReceivedDate.strftime("%Y-%m-%dT%H:%M:%S")),
    headers={"X-Api-Key": str(apiToken)},
)
if response.status_code == 200:
    if len(response.json()) > 0:
        for message in response.json():
            deviceGuid = str(message["deviceGuid"])
            messageGuid = str(message["messageGuid"])
            latitude = message["latitude"]
            longitude = message["longitude"]
            payload = base64.b64decode(message["data"]).hex()
            ascii_payload = base64.b64decode(message["data"]).decode("utf-8")
            print(ascii_payload)
            print()
    else:
        print("There is no message.")
else:
    print("Error, something is wrong in the request.")

# Encapsulate above into a function that is a background process. The process
# should run every 5 minutes to check for new messages and can be called to
# check for new messages and get the time until the next check.


async def get_astrocast_messages():
    """Get the latest messages from the Astrocast API"""
    # Get the latest messages from the Astrocast API
