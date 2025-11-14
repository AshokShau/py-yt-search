import asyncio

from py_yt import Playlist, Video, Transcript, Channel, Suggestions, Hashtag
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

    async with Playlist(
        "https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK"
    ) as playlist:
        while playlist.hasMoreVideos:
            print("Getting more videos...")
            await playlist.getNextVideos()
            print(f"Videos Retrieved: {len(playlist.videos)}")

    print("Playlist Videos " + str(playlist.videos))

    """
    Can be used to get search results with custom defined filters.

    Setting second parameter as VideoSortOrder.uploadDate, to get video results sorted according to upload date.

    Few of the predefined filters for you to use are:
    SearchMode.videos
    VideoUploadDateFilter.lastHour
    VideoDurationFilter.long
    VideoSortOrder.viewCount
    There are many other for you to check out.

    If this much control isn't enough then, you may pass custom string yourself by seeing the YouTube query in any web browser e.g. 
    "EgQIBRAB" from "https://www.youtube.com/results?search_query=NoCopyrightSounds&sp=EgQIBRAB" may be passed as second parameter to get only videos, which are uploaded this year.
    """
    async with CustomSearch(
        "NoCopyrightSounds", VideoSortOrder.uploadDate, language="en", region="US"
    ) as customSearch:
        customResult = await customSearch.next()
        print("Custom Search" + str(customResult))

    async with ChannelSearch("Watermelon Sugar", "UCZFWPqqPkFlNwIxcpsLOwew") as _search:
        result = await _search.next()
        print("Channel Search" + str(result))

    """
    Getting search results from the next pages on YouTube.
    Generally you'll get maximum of 20 videos in one search, for getting subsequent results, you may call `next` method.
    """
    async with VideosSearch("NoCopyrightSounds") as _search:
        index = 0
        """ Getting result on 1st page """
        result = await _search.next()
        """ Displaying the result """
        print("Videos Search" + str(result))
        for video in result["result"]:
            index += 1
            print(f'{index} - {video["title"]}')
        """ Getting result on 2nd page """
        result = await _search.next()
        """ Displaying the result """
        for video in result["result"]:
            index += 1
            print(f'{index} - {video["title"]}')
        """ Getting result on 3rd page """
        result = await _search.next()
        """ Displaying the result """
        for video in result["result"]:
            index += 1
            print(f'{index} - {video["title"]}')

    """
    Getting information about video or its formats using video link or video ID.

    `Video.get` method will give both information & formats of the video
    `Video.getInfo` method will give only information about the video.
    `Video.getFormats` method will give only formats of the video.

    You may either pass link or ID, method will take care itself.
    """
    video = await Video.get("z0GKGpObgPY")
    print("Video" + str(video))
    videoInfo = await Video.getInfo("https://youtu.be/z0GKGpObgPY")
    print("Video Info" + str(videoInfo))

    """
    Getting search suggestions from YouTube.
    You may show search suggestions to users before making any search.
    """
    suggestions = await Suggestions.get("NoCopyrightSounds", language="en", region="US")
    print("Suggestions" + str(suggestions))

    """
    Getting videos by hashtag.
    """
    async with Hashtag("ncs", limit=1) as hashtag:
        result = await hashtag.next()
        print("Hashtag" + str(result))


    print(await Transcript.get("https://www.youtube.com/watch?v=L7kF4MXXCoA"))
    url = "https://www.youtube.com/watch?v=-1xu0IP35FI"

    transcript_en = await Transcript.get(url)
    transcript_2 = await Transcript.get(
        url, transcript_en["languages"][-1]["params"]
    )
    print(transcript_2)
    print(await Channel.get("UC_aEa8K-EOJ3D6gOs7HcyNg"))
    # Retrieve playlists of a channel
    async with Channel("UC_aEa8K-EOJ3D6gOs7HcyNg") as channel:
        await channel.init()
        print(len(channel.result["playlists"]))
        while channel.has_more_playlists():
            await channel.next()
            print(len(channel.result["playlists"]))


if __name__ == "__main__":
    asyncio.run(main())
