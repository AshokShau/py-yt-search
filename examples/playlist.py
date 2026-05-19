import asyncio
from py_yt import Playlist, close_session

async def main():
    """
    Getting information about playlist or videos in it using link.

    `Playlist.get` method will give both information & videos in the playlist
    `Playlist.getInfo` method will give only information about the playlist.
    `Playlist.getFormats` method will give only formats of the playlist.

    """
    playlist_url = "https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK"
    
    playlist_full = await Playlist.get(playlist_url)
    print(playlist_full)
    
    playlistInfo = await Playlist.getInfo(playlist_url)
    print(playlistInfo)
    
    playlistVideos = await Playlist.getVideos(playlist_url)
    print(playlistVideos)

    """
    More tests to buggy Playlist class
    """
    playlist_buggy = await Playlist.get(
        "https://www.youtube.com/watch?v=bplUXwTTgbI&list=PL6edxAMqu2xfxgbf7Q09hSg1qCMfDI7IZ"
    )
    print(playlist_buggy)

    """
    Fetching more videos from a playlist
    """
    playlist_iter = Playlist(playlist_url)

    while playlist_iter.hasMoreVideos:
        print("Getting more videos...")
        await playlist_iter.getNextVideos()
        print(f"Videos Retrieved: {len(playlist_iter.videos)}")

    print("Found all the videos.")

    await close_session()

if __name__ == "__main__":
    asyncio.run(main())