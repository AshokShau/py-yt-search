import asyncio
from py_yt.search import ChannelSearch

async def main():
    print("Testing ChannelSearch...")
    # Harry Styles channel ID: UCZFWPqqPkFlNwIxcpsLOwew
    # Searching for "Watermelon Sugar"
    search = ChannelSearch('Watermelon Sugar', "UCZFWPqqPkFlNwIxcpsLOwew")
    try:
        result = await search.next()
        print(f"ChannelSearch Result keys: {result.keys()}")
        if "result" in result:
             print("ChannelSearch Result: Success (Structure correct)")
             print(f"Count: {len(result['result'])}")
             if len(result['result']) > 0:
                 print(result['result'][0])
        else:
             print("ChannelSearch Result: Failed structure")
             print(result)
    except Exception as e:
        print(f"ChannelSearch Failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
