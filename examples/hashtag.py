import asyncio
from py_yt import Hashtag

async def main():
    """
    Getting videos by hashtag.
    """
    print("--- Hashtag Search ---")
    hashtag = Hashtag("ncs", limit=1)
    result = await hashtag.next()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
