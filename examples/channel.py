import asyncio
import json
from py_yt import Channel

async def main():
    """
    Retrieve playlists of a channel
    """
    async with Channel("UC_aEa8K-EOJ3D6gOs7HcyNg") as channel:
        print(json.dumps(channel.result, indent=4))

if __name__ == "__main__":
    asyncio.run(main())
