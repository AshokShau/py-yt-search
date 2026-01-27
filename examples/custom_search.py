import asyncio
from py_yt import CustomSearch
from py_yt.core.constants import VideoSortOrder

async def main():
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
    print("--- Custom Search ---")
    customSearch = CustomSearch(
        "NoCopyrightSounds", VideoSortOrder.uploadDate, language="en", region="US"
    )
    customResult = await customSearch.next()
    print(customResult)

if __name__ == "__main__":
    asyncio.run(main())
