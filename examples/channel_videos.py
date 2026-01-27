import asyncio
from py_yt.extras import Channel
from py_yt.core.constants import ChannelRequestType


async def main():
    channel_id = "UC_aEa8K-EOJ3D6gOs7HcyNg"  # NCS House
    print(f"Fetching videos for channel: {channel_id}")

    try:
        channel = Channel(channel_id, ChannelRequestType.videos)
        await channel.async_create()
        result = channel.result

        print("Channel Info:")
        print(f"Title: {result.get('title')}")

        videos = result.get('videos', [])
        print(f"Found {len(videos)} videos.")

        if len(videos) > 0:
            print("First video:")
            print(videos[0])

        if channel.has_more_videos():
            print("Has more videos. Fetching next page...")
            await channel.next()
            result = channel.result
            videos = result.get('videos', [])
            print(f"Total videos after next page: {len(videos)}")
        else:
            print("No more videos.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
