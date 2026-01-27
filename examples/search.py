import asyncio
from py_yt import Search, VideosSearch, ChannelsSearch, PlaylistsSearch

async def main():
    """
    Searches for all types of results like videos, channels & playlists in YouTube.
    'type' key in the JSON/Dictionary may be used to differentiate between the types of result.
    """
    print("--- Search (All types) ---")
    _search = Search("NoCopyrightSounds", limit=1, language="en", region="US")
    result = await _search.next()
    print(result)

    """
    Searches only for videos in YouTube.
    """
    print("\n--- Videos Search ---")
    videosSearch = VideosSearch(
        "NoCopyrightSounds", limit=10, language="en", region="US"
    )
    videosResult = await videosSearch.next()
    print(videosResult)

    """
    Searches only for channels in YouTube.
    """
    print("\n--- Channels Search ---")
    channelsSearch = ChannelsSearch(
        "NoCopyrightSounds", limit=1, language="en", region="US"
    )
    channelsResult = await channelsSearch.next()
    print(channelsResult)

    """
    Searches only for playlists in YouTube.
    """
    print("\n--- Playlists Search ---")
    playlistsSearch = PlaylistsSearch(
        "NoCopyrightSounds", limit=1, language="en", region="US"
    )
    playlistsResult = await playlistsSearch.next()
    print(playlistsResult)

if __name__ == "__main__":
    asyncio.run(main())
