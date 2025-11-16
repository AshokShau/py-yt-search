import asyncio

from py_yt import Playlist

async def main():
    """
    Fetches information and videos for the given playlist link.
    """
    async with Playlist(
        "https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK"
    ) as playlist:
        while playlist.hasMoreVideos:
            print("Getting more videos...")
            await playlist.getNextVideos()
            print(f"Videos Retrieved: {len(playlist.videos)}")

    print("Playlist Videos " + str(playlist.videos))

if __name__ == "__main__":
    asyncio.run(main())
