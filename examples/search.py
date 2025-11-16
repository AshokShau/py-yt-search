import asyncio

from py_yt import (
    Search,
    VideosSearch,
    ChannelsSearch,
    PlaylistsSearch,
    CustomSearch,
    ChannelSearch,
)
from py_yt.core.constants import VideoSortOrder

async def main():
    """
    Searches for all types of results like videos, channels & playlists in YouTube.
    'type' key in the JSON/Dictionary may be used to differentiate between the types of result.
    """
    async with Search("NoCopyrightSounds", limit=1, language="en", region="US") as _search:
        result = await _search.next()
        print("Search " + str(result))

    """
    Searches only for videos in YouTube.
    """
    async with VideosSearch(
        "NoCopyrightSounds", limit=10, language="en", region="US"
    ) as videosSearch:
        videosResult = await videosSearch.next()
        print("Videos Search " + str(videosResult))

    """
    Searches only for channels in YouTube.
    """
    async with ChannelsSearch(
        "NoCopyrightSounds", limit=1, language="en", region="US"
    ) as channelsSearch:
        channelsResult = await channelsSearch.next()
        print("Channels Search " + str(channelsResult))

    """
    Searches only for playlists in YouTube.
    """
    async with PlaylistsSearch(
        "NoCopyrightSounds", limit=1, language="en", region="US"
    ) as playlistsSearch:
        playlistsResult = await playlistsSearch.next()
        print("Playlists Search " + str(playlistsResult))

    """
    Can be used to get search results with custom defined filters.
    """
    async with CustomSearch(
        "NoCopyrightSounds", VideoSortOrder.uploadDate, language="en", region="US"
    ) as customSearch:
        customResult = await customSearch.next()
        print("Custom Search" + str(customResult))

    async with ChannelSearch("Watermelon Sugar", "UCZFWPqqPkFlNwIxcpsLOwew") as _search:
        result = await _search.next()
        print("Channel Search" + str(result))

if __name__ == "__main__":
    asyncio.run(main())
