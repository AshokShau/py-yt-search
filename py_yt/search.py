from typing import Any, Callable, Dict, Optional

from py_yt.core.channelsearch import ChannelSearchCore
from py_yt.core.constants import SearchMode
from py_yt.core.search import SearchCore


class Search(SearchCore):
    """Searches for videos, channels & playlists in YouTube."""

    def __init__(
        self,
        query: str,
        limit: int = 20,
        language: str = "en",
        region: str = "US",
        timeout: Optional[float] = None,
        with_live: bool = True,
        max_retries: int = 2,
        proxy: Optional[str] = None,
        visitor_data: Optional[str] = None,
        po_token: Optional[str] = None,
        po_token_verifier: Optional[Callable[..., Any]] = None,
    ) -> None:
        self.searchMode = (True, True, True)
        super().__init__(
            query,
            limit,
            language,
            region,
            "",
            timeout if timeout is not None else 7.0,
            with_live=with_live,
            max_retries=max_retries,
            proxy=proxy,
            visitor_data=visitor_data,
            po_token=po_token,
            po_token_verifier=po_token_verifier,
        )

    async def next(self) -> Dict[str, Any]:
        return await super().next()


class VideosSearch(SearchCore):
    """Searches for videos in YouTube."""

    def __init__(
        self,
        query: str,
        limit: int = 20,
        language: str = "en",
        region: str = "US",
        timeout: Optional[float] = None,
        with_live: bool = True,
        max_retries: int = 2,
        proxy: Optional[str] = None,
        visitor_data: Optional[str] = None,
        po_token: Optional[str] = None,
        po_token_verifier: Optional[Callable[..., Any]] = None,
    ) -> None:
        self.searchMode = (True, False, False)
        super().__init__(
            query,
            limit,
            language,
            region,
            SearchMode.videos,
            timeout if timeout is not None else 7.0,
            with_live=with_live,
            max_retries=max_retries,
            proxy=proxy,
            visitor_data=visitor_data,
            po_token=po_token,
            po_token_verifier=po_token_verifier,
        )

    async def next(self) -> Dict[str, Any]:
        return await super().next()


class ChannelsSearch(SearchCore):
    """Searches for channels in YouTube."""

    def __init__(
        self,
        query: str,
        limit: int = 20,
        language: str = "en",
        region: str = "US",
        timeout: Optional[float] = None,
        max_retries: int = 2,
        proxy: Optional[str] = None,
        visitor_data: Optional[str] = None,
        po_token: Optional[str] = None,
        po_token_verifier: Optional[Callable[..., Any]] = None,
    ) -> None:
        self.searchMode = (False, True, False)
        super().__init__(
            query,
            limit,
            language,
            region,
            SearchMode.channels,
            timeout if timeout is not None else 7.0,
            max_retries=max_retries,
            proxy=proxy,
            visitor_data=visitor_data,
            po_token=po_token,
            po_token_verifier=po_token_verifier,
        )

    async def next(self) -> Dict[str, Any]:
        return await super().next()


class PlaylistsSearch(SearchCore):
    """Searches for playlists in YouTube."""

    def __init__(
        self,
        query: str,
        limit: int = 20,
        language: str = "en",
        region: str = "US",
        timeout: Optional[float] = None,
        max_retries: int = 2,
        proxy: Optional[str] = None,
        visitor_data: Optional[str] = None,
        po_token: Optional[str] = None,
        po_token_verifier: Optional[Callable[..., Any]] = None,
    ) -> None:
        self.searchMode = (False, False, True)
        super().__init__(
            query,
            limit,
            language,
            region,
            SearchMode.playlists,
            timeout if timeout is not None else 7.0,
            max_retries=max_retries,
            proxy=proxy,
            visitor_data=visitor_data,
            po_token=po_token,
            po_token_verifier=po_token_verifier,
        )

    async def next(self) -> Dict[str, Any]:
        return await super().next()


class CustomSearch(SearchCore):
    """Performs custom search in YouTube with search filters or sorting orders."""

    def __init__(
        self,
        query: str,
        search_preferences: str,
        limit: int = 20,
        language: str = "en",
        region: str = "US",
        timeout: Optional[float] = None,
        with_live: bool = True,
        max_retries: int = 2,
        proxy: Optional[str] = None,
        visitor_data: Optional[str] = None,
        po_token: Optional[str] = None,
        po_token_verifier: Optional[Callable[..., Any]] = None,
    ) -> None:
        self.searchMode = (True, True, True)
        super().__init__(
            query,
            limit,
            language,
            region,
            search_preferences,
            timeout if timeout is not None else 7.0,
            with_live=with_live,
            max_retries=max_retries,
            proxy=proxy,
            visitor_data=visitor_data,
            po_token=po_token,
            po_token_verifier=po_token_verifier,
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
        timeout: Optional[float] = None,
        max_retries: int = 2,
        proxy: Optional[str] = None,
        visitor_data: Optional[str] = None,
        po_token: Optional[str] = None,
        po_token_verifier: Optional[Callable[..., Any]] = None,
    ) -> None:
        super().__init__(
            query,
            language,
            region,
            search_preferences,
            browse_id,
            timeout if timeout is not None else 7.0,
            max_retries=max_retries,
            proxy=proxy,
            visitor_data=visitor_data,
            po_token=po_token,
            po_token_verifier=po_token_verifier,
        )

    async def next(self) -> Dict[str, Any]:
        return await super().next()
