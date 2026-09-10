import asyncio

from py_yt import Transcript, close_session


async def main():
    """
    Retrieving video transcripts using video link or video ID.

    You can use:
    - `Transcript.get(video_link)`
    - `Transcript.get_transcript(video_link)`
    - `get_transcript(video_link)`

    Returns a dictionary with keys:
    - `segments`: List of transcript text segments with timestamps
    - `languages`: List of available transcript languages
    """
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    print("Fetching transcript using Transcript.get...")
    transcript = await Transcript.get(video_url)
    print(f"Result keys: {list(transcript.keys())}")
    print(f"Segments count: {len(transcript.get('segments', []))}")
    print(f"Languages count: {len(transcript.get('languages', []))}")
    if transcript.get("segments"):
        print(f"segment: {transcript['segments'][0]}")
        # print(transcript1)

    await close_session()


if __name__ == "__main__":
    asyncio.run(main())
