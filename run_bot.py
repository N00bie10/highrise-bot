from highrise.__main__ import main
import asyncio
import os
from bot import HighriseRoomBot

ROOM_ID = os.getenv("693df3b1a855b7d3cd87e0fb")
API_TOKEN = os.getenv("59a326bf94f286d0c3649e22e49505c66c134e5e6d57983e90fd9eeca721b20b")

definitions = {
    ROOM_ID: HighriseRoomBot
}

asyncio.run(main(definitions))
