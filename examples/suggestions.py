import asyncio
from py_yt import Suggestions, close_session

async def main():
    """
    Getting search suggestions from YouTube.
    You may show search suggestions to users before making any search.
    """
    suggestions = await Suggestions.get("NoCopyrightSounds", language="en", region="US")
    print(suggestions)

    await close_session()

if __name__ == "__main__":
    asyncio.run(main())