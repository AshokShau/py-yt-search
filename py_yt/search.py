from typing import Any, Dict, Optional

from py_yt.core.channelsearch import ChannelSearchCore
from py_yt.core.constants import VideoSortOrder, SearchMode
from py_yt.core.search import SearchCore


class Search(SearchCore):
    """Searches for videos, channels & playlists in YouTube.

    Args:
        query (str): Sets the search query.
        limit (int, optional): Sets limit to the number of results. Defaults to 20.
        language (str, optional): Sets the result language. Defaults to 'en'.
        region (str, optional): Sets the result region. Defaults to 'US'.

    Examples:
        Calling `result` method gives the search result.

        >>> search = Search('Watermelon Sugar', limit = 1)
        >>> result = await search.next()
        >>> print(result)
        {
            "result": [
                {
                    "type": "video",
                    "id": "E07s5ZYygMg",
                    "title": "Harry Styles - Watermelon Sugar (Official Video)",
                    "publishedTime": "6 months ago",
                    "duration": "3:09",
                    "viewCount": {
                        "text": "162,235,006 views",
                        "short": "162M views"
                    },
                    "thumbnails": [
                        {
                            "url": "https://i.ytimg.com/vi/E07s5ZYygMg/hq720.jpg?sqp=-oaymwEjCOgCEMoBSFryq4qpAxUIARUAAAAAGAElAADIQj0AgKJDeAE=&rs=AOn4CLAOWBTE1SDrtrDQ1aWNzpDZ7YiMIw",
                            "width": 360,
                            "height": 202
                        },
                        {
                            "url": "https://i.ytimg.com/vi/E07s5ZYygMg/hq720.jpg?sqp=-oaymwEXCNAFEJQDSFryq4qpAwkIARUAAIhCGAE=&rs=AOn4CLD7U54pGZLPKTuMP-J3kpm4LIDPVg",
                            "width": 720,
                            "height": 404
                        }
                    ],
                    "descriptionSnippet": [
                        {
                            "text": "This video is dedicated to touching. Listen to Harry Styles' new album 'Fine Line' now: https://HStyles.lnk.to/FineLineAY Follow\u00a0..."
                        }
                    ],
                    "channel": {
                        "name": "Harry Styles",
                        "id": "UCZFWPqqPkFlNwIxcpsLOwew",
                        "thumbnails": [
                            {
                                "url": "https://yt3.ggpht.com/a-/AOh14GgNUvHxwlnz4RpHamcGnZF1px13VHj01TPksw=s68-c-k-c0x00ffffff-no-rj-mo",
                                "width": 68,
                                "height": 68
                            }
                        ],
                        "link": "https://www.youtube.com/channel/UCZFWPqqPkFlNwIxcpsLOwew"
                    },
                    "accessibility": {
                        "title": "Harry Styles - Watermelon Sugar (Official Video) by Harry Styles 6 months ago 3 minutes, 9 seconds 162,235,006 views",
                        "duration": "3 minutes, 9 seconds"
                    },
                    "link": "https://www.youtube.com/watch?v=E07s5ZYygMg",
                    "shelfTitle": null
                }
            ]
        }
    """

    def __init__(
        self,
        query: str,
        limit: int = 20,
        language: str = "en",
        region: str = "US",
        timeout: Optional[int] = None,
        with_live: bool = True,
        max_retries: int = 0,
        proxy: str | None = None,
    ):
        self.searchMode = (True, True, True)
        super().__init__(
            query,
            limit,
            language,
            region,
            None,
            timeout,
            with_live=with_live,
            max_retries=max_retries,
            proxy=proxy,
        )  # type: ignore

    async def next(self) -> Dict[str, Any]:
        return await super().next()  # type: ignore


class VideosSearch(SearchCore):
    """Searches for videos in YouTube."""

    def __init__(
        self,
        query: str,
        limit: int = 20,
        language: str = "en",
        region: str = "US",
        timeout: Optional[int] = None,
        with_live: bool = True,
        max_retries: int = 0,
        proxy: str | None = None,
    ):
        self.searchMode = (True, False, False)
        super().__init__(
            query,
            limit,
            language,
            region,
            SearchMode.videos,
            timeout,
            with_live=with_live,
            max_retries=max_retries,
            proxy=proxy,
        )

    async def next(self) -> Dict[str, Any]:
        return await super().next()  # type: ignore


class ChannelsSearch(SearchCore):
    """Searches for channels in YouTube."""

    def __init__(
        self,
        query: str,
        limit: int = 20,
        language: str = "en",
        region: str = "US",
        timeout: Optional[int] = None,
        max_retries: int = 0,
        proxy: str | None = None,
    ):
        self.searchMode = (False, True, False)
        super().__init__(
            query,
            limit,
            language,
            region,
            SearchMode.channels,
            timeout,
            max_retries=max_retries,
            proxy=proxy,
        )  # type: ignore

    async def next(self) -> Dict[str, Any]:
        return await super().next()  # type: ignore


class PlaylistsSearch(SearchCore):
    """Searches for playlists in YouTube."""

    def __init__(
        self,
        query: str,
        limit: int = 20,
        language: str = "en",
        region: str = "US",
        timeout: Optional[int] = None,
        max_retries: int = 0,
        proxy: str | None = None,
    ):
        self.searchMode = (False, False, True)
        super().__init__(
            query,
            limit,
            language,
            region,
            SearchMode.playlists,
            timeout,
            max_retries=max_retries,
            proxy=proxy,
        )  # type: ignore

    async def next(self) -> Dict[str, Any]:
        return await super().next()  # type: ignore


class CustomSearch(SearchCore):
    """Performs custom search in YouTube with search filters or sorting orders."""

    def __init__(
        self,
        query: str,
        search_preferences: str,
        limit: int = 20,
        language: str = "en",
        region: str = "US",
        timeout: Optional[int] = None,
        with_live: bool = True,
        max_retries: int = 0,
        proxy: str | None = None,
    ):
        self.searchMode = (True, True, True)
        super().__init__(
            query,
            limit,
            language,
            region,
            search_preferences,
            timeout,
            with_live=with_live,
            max_retries=max_retries,
            proxy=proxy,
        )

    async def next(self) -> Dict[str, Any]:
        return await super().next()


class ChannelSearch(ChannelSearchCore):
    """Searches for videos in specific channel in YouTube."""

    def __init__(
        self,
        query: str,
        browse_id: str,
        language: str = "en",
        region: str = "US",
        search_preferences: str = "EgZzZWFyY2g%3D",
        timeout: Optional[int] = None,
        max_retries: int = 0,
        proxy: str | None = None,
    ):
        super().__init__(
            query,
            language,
            region,
            search_preferences,
            browse_id,
            timeout,
            max_retries=max_retries,
            proxy=proxy,
        )  # type: ignore

    async def next(self):
        return await super().next()
