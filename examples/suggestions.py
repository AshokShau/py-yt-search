import asyncio
from py_yt import Suggestions

async def main():
    """
    Getting search suggestions from YouTube.
    You may show search suggestions to users before making any search.
    """
    print("--- Suggestions ---")
    suggestions = await Suggestions.get("NoCopyrightSounds", language="en", region="US")
    print(suggestions)

if __name__ == "__main__":
    asyncio.run(main())
