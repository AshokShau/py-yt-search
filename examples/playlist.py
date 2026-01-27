import asyncio
from py_yt import Playlist

async def main():
    print("--- Playlist Details ---")
    playlist = Playlist(
        "https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK"
    )
    while playlist.hasMoreVideos:
        print("Getting more videos...")
        await playlist.getNextVideos()
        print(f"Videos Retrieved: {len(playlist.videos)}")

    print("Found all the videos.")

    """
    Getting information about playlist or videos in it using link.

    `Playlist.get` method will give both information & videos in the playlist
    `Playlist.getInfo` method will give only information about the playlist.
    `Playlist.getFormats` method will give only formats of the playlist. (Note: getFormats might not be applicable for Playlist, need to check, but following original example)
    """
    print("\n--- Playlist.get ---")
    playlist_data = await Playlist.get(
        "https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK"
    )
    print(playlist_data)

    print("\n--- Playlist.getInfo ---")
    playlistInfo = await Playlist.getInfo(
        "https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK"
    )
    print(playlistInfo)

    print("\n--- Playlist.getVideos ---")
    playlistVideos = await Playlist.getVideos(
        "https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK"
    )
    print(playlistVideos)
    
    # Additional tests from original example
    print("\n--- Additional Playlist Tests ---")
    playlist_res = await Playlist.get(
        "https://www.youtube.com/watch?v=bplUXwTTgbI&list=PL6edxAMqu2xfxgbf7Q09hSg1qCMfDI7IZ"
    )
    print(playlist_res)


if __name__ == "__main__":
    asyncio.run(main())
