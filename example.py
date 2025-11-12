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
    _search = Search("NoCopyrightSounds", limit=1, language="en", region="US")
    result = await _search.next()
    print(result)

    """
    Searches only for videos in YouTube.
    """
    videosSearch = VideosSearch(
        "NoCopyrightSounds", limit=10, language="en", region="US"
    )
    videosResult = await videosSearch.next()
    print(videosResult)

    """
    Searches only for channels in YouTube.
    """
    channelsSearch = ChannelsSearch(
        "NoCopyrightSounds", limit=1, language="en", region="US"
    )
    channelsResult = await channelsSearch.next()
    print(channelsResult)

    """
    Searches only for playlists in YouTube.
    """
    playlistsSearch = PlaylistsSearch(
        "NoCopyrightSounds", limit=1, language="en", region="US"
    )
    playlistsResult = await playlistsSearch.next()
    print(playlistsResult)

    playlist = Playlist(
        "https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK"
    )
    while playlist.hasMoreVideos:
        print("Getting more videos...")
        await playlist.getNextVideos()
        print(f"Videos Retrieved: {len(playlist.videos)}")

    print("Found all the videos.")

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
    customSearch = CustomSearch(
        "NoCopyrightSounds", VideoSortOrder.uploadDate, language="en", region="US"
    )
    customResult = await customSearch.next()
    print(customResult)

    _search = ChannelSearch("Watermelon Sugar", "UCZFWPqqPkFlNwIxcpsLOwew")
    result = await _search.next()
    print(result)

    """
    Getting search results from the next pages on YouTube.
    Generally you'll get maximum of 20 videos in one search, for getting subsequent results, you may call `next` method.
    """
    _search = VideosSearch("NoCopyrightSounds")
    index = 0
    """ Getting result on 1st page """
    result = await _search.next()
    """ Displaying the result """
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
    print(video)
    videoInfo = await Video.getInfo("https://youtu.be/z0GKGpObgPY")
    print(videoInfo)

    videoInfo = await Video.getInfo("https://music.youtube.com/watch?v=RLsYNh7GN-k&si=tgb4LsBN8zEU-iST")
    print(videoInfo)

    """
    Getting information about playlist or videos in it using link.

    `Playlist.get` method will give both information & videos in the playlist
    `Playlist.getInfo` method will give only information about the playlist.
    `Playlist.getFormats` method will give only formats of the playlist.

    """
    playlist = await Playlist.get(
        "https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK"
    )
    print(playlist)
    playlistInfo = await Playlist.getInfo(
        "https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK"
    )
    print(playlistInfo)
    playlistVideos = await Playlist.getVideos(
        "https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK"
    )
    print(playlistVideos)

    """
    More tests to buggy Playlist class
    """
    playlist = await Playlist.get(
        "https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK"
    )
    print(playlist)
    playlist = await Playlist.get(
        "https://www.youtube.com/watch?v=bplUXwTTgbI&list=PL6edxAMqu2xfxgbf7Q09hSg1qCMfDI7IZ"
    )
    print(playlist)

    """
    Getting search suggestions from YouTube.
    You may show search suggestions to users before making any search.
    """
    suggestions = await Suggestions.get("NoCopyrightSounds", language="en", region="US")
    print(suggestions)

    """
    Getting videos by hashtag.
    """
    hashtag = Hashtag("ncs", limit=1)
    result = await hashtag.next()
    print(result)

    print(await Transcript.get("https://www.youtube.com/watch?v=L7kF4MXXCoA"))

    url = "https://www.youtube.com/watch?v=-1xu0IP35FI"

    transcript_en = await Transcript.get(url)
    # you actually don't have to pass a valid URL in following Transcript call. You can input an empty string, but I do recommend still inputing a valid URL.
    transcript_2 = await Transcript.get(
        url, transcript_en["languages"][-1]["params"]
    )  # in my case, it'd output Spanish.
    print(transcript_2)

    print(await Channel.get("UC_aEa8K-EOJ3D6gOs7HcyNg"))

    # Retrieve playlists of a channel
    channel = Channel("UC_aEa8K-EOJ3D6gOs7HcyNg")
    await channel.init()
    print(len(channel.result["playlists"]))
    while channel.has_more_playlists():
        await channel.next()
        print(len(channel.result["playlists"]))


if __name__ == "__main__":
    asyncio.run(main())

