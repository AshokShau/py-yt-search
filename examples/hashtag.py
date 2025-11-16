import asyncio
import json
from py_yt import Hashtag

async def main():
    """
    Getting videos by hashtag.
    """
    async with Hashtag("ncs", limit=1) as hashtag:
        result = await hashtag.next()
        print(json.dumps(result, indent=4))

if __name__ == "__main__":
    asyncio.run(main())
