import asyncio
from py_yt import Search, VideosSearch, ChannelsSearch, PlaylistsSearch, close_session

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

    """
    Getting search results from the next pages on YouTube.
    Generally you'll get maximum of 20 videos in one search, for getting subsequent results, you may call `next` method.
    """
    _search_pages = VideosSearch("NoCopyrightSounds")
    index = 0
    """ Getting result on 1st page """
    result_page1 = await _search_pages.next()
    """ Displaying the result """
    for video in result_page1.get("result", []):
        index += 1
        print(f'{index} - {video.get("title", "No Title")}')
        
    """ Getting result on 2nd page """
    result_page2 = await _search_pages.next()
    """ Displaying the result """
    for video in result_page2.get("result", []):
        index += 1
        print(f'{index} - {video.get("title", "No Title")}')
        
    """ Getting result on 3rd page """
    result_page3 = await _search_pages.next()
    """ Displaying the result """
    for video in result_page3.get("result", []):
        index += 1
        print(f'{index} - {video.get("title", "No Title")}')

    await close_session()

if __name__ == "__main__":
    asyncio.run(main())