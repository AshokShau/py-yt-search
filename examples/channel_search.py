import asyncio
from py_yt import ChannelSearch

async def main():
    """
    Searches for videos within a specific channel.
    """
    _search = ChannelSearch("Watermelon Sugar", "UCZFWPqqPkFlNwIxcpsLOwew")
    result = await _search.next()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())