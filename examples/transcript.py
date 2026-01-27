import asyncio
from py_yt import Transcript

async def main():
    print("--- Transcript ---")
    try:
        print(await Transcript.get("https://www.youtube.com/watch?v=L7kF4MXXCoA"))
    except Exception as e:
        print(f"Failed to get transcript for L7kF4MXXCoA: {e}")

    url = "https://www.youtube.com/watch?v=-1xu0IP35FI"
    print(f"\nGetting transcript for {url}")
    try:
        transcript_en = await Transcript.get(url)
        
        if transcript_en and "languages" in transcript_en and len(transcript_en["languages"]) > 0:
            # you actually don't have to pass a valid URL in following Transcript call. You can input an empty string, but I do recommend still inputing a valid URL.
            transcript_2 = await Transcript.get(
                url, transcript_en["languages"][-1]["params"]
            ) 
            print(transcript_2)
        else:
            print("No languages found or transcript failed.")
    except Exception as e:
        print(f"Failed to get transcript for {url}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
