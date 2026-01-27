import asyncio
from py_yt import Video

async def main():
    """
    Getting information about video or its formats using video link or video ID.

    `Video.get` method will give both information & formats of the video
    `Video.getInfo` method will give only information about the video.
    `Video.getFormats` method will give only formats of the video.

    You may either pass link or ID, method will take care itself.
    """
    print("--- Video.get ---")
    video = await Video.get("z0GKGpObgPY")
    print(video)

    print("\n--- Video.getInfo ---")
    videoInfo = await Video.getInfo("https://youtu.be/z0GKGpObgPY")
    print(videoInfo)

    print("\n--- Video.getInfo (Music) ---")
    videoInfo = await Video.getInfo("https://music.youtube.com/watch?v=RLsYNh7GN-k&si=tgb4LsBN8zEU-iST")
    print(videoInfo)

if __name__ == "__main__":
    asyncio.run(main())
