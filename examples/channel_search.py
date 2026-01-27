import asyncio
from py_yt import ChannelSearch

async def main():

    print("--- Channel Search ---")
    # Searching for "Watermelon Sugar" inside channel with ID "UCZFWPqqPkFlNwIxcpsLOwew"
    _search = ChannelSearch("Watermelon Sugar", "UCZFWPqqPkFlNwIxcpsLOwew")
    result = await _search.next()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
