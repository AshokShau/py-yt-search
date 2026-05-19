import asyncio
from py_yt import Hashtag, close_session

async def main():
    """
    Getting videos by hashtag.
    """
    hashtag = Hashtag("ncs", limit=1)
    result = await hashtag.next()
    print(result)

    await close_session()

if __name__ == "__main__":
    asyncio.run(main())