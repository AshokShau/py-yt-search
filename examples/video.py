import asyncio

from py_yt import Video

async def main():
    """
    Getting information about video or its formats using video link or video ID.
    `Video.get` method will give both information & formats of the video; deprecated.
    `Video.getInfo` method will give only information about the video.
    `Video.getFormats` method will give only formats of the video.; deprecated.
    You may either pass link or ID, method will take care itself.
    """
    video = await Video.getInfo("z0GKGpObgPY")
    print("Video" + str(video))
    videoInfo = await Video.getInfo("https://youtu.be/z0GKGpObgPY")
    print("Video Info" + str(videoInfo))
    videoFormats = await Video.getFormats("z0GKGpObgPY")
    print("Video Formats" + str(videoFormats))
    videoFormats = await Video.getFormats("https://youtu.be/z0GKGpObgPY")
    print("Video Formats" + str(videoFormats))

if __name__ == "__main__":
    asyncio.run(main())
