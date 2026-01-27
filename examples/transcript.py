import asyncio
from py_yt.extras import Transcript

async def main():
    print("Testing Transcript...")
    # Video ID: E07s5ZYygMg (Harry Styles - Watermelon Sugar)
    video_link = "https://www.youtube.com/watch?v=E07s5ZYygMg"
    try:
        result = await Transcript.get(video_link)
        print(f"Transcript Result keys: {result.keys()}")
        if "segments" in result:
             print("Transcript Result: Success (Structure correct)")
             print(f"Segments count: {len(result['segments'])}")
        else:
             print("Transcript Result: Empty or Failed")
             print(result)

    except Exception as e:
        print(f"Transcript Failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
