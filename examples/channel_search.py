import asyncio
from py_yt import ChannelSearch, close_session

async def main():
    """
    Searches for videos within a specific channel.
    """
    _search = ChannelSearch("Watermelon Sugar", "UCZFWPqqPkFlNwIxcpsLOwew")
    result = await _search.next()
    print(result)

    await close_session()

if __name__ == "__main__":
    asyncio.run(main())