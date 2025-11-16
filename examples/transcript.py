import asyncio

from py_yt import Transcript

async def main():
    """
    Getting transcripts from YouTube.
    """
    transcript = await Transcript.get("https://www.youtube.com/watch?v=L7kF4MXXCoA")
    print(transcript)
    url = "https://www.youtube.com/watch?v=-1xu0IP35FI"

    transcript_en = await Transcript.get(url)
    transcript_2 = await Transcript.get(
        url, transcript_en["languages"][-1]["params"]
    )
    print(transcript_2)

if __name__ == "__main__":
    asyncio.run(main())
