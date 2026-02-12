from asyncio import run as asyncio_run
from highrise.__main__ import BotDefinition, main
from bot import HighriseRoomBot

ROOM_ID = "693df3b1a855b7d3cd87e0fb"
API_TOKEN = "59a326bf94f286d0c3649e22e49505c66c134e5e6d57983e90fd9eeca721b20b"

definitions = [
    BotDefinition(HighriseRoomBot(), ROOM_ID, API_TOKEN)
]

asyncio_run(main(definitions))
