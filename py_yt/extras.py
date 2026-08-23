import copy
from typing import Any, Dict, List, Optional, Union

from py_yt.core.browse import BrowseCore
from py_yt.core.channel import ChannelCore
from py_yt.core.constants import ChannelRequestType, ResultMode
from py_yt.core.hashtag import HashtagCore
from py_yt.core.playlist import PlaylistCore
from py_yt.core.recommendations import RelatedVideosCore
from py_yt.core.suggestions import SuggestionsCore
from py_yt.core.transcript import TranscriptCore
from py_yt.core.video import VideoCore


class Video:
    @staticmethod
    async def get(
        video_link: str,
        result_mode: int = ResultMode.dict,
        timeout: float = 2.0,
        get_upload_date: bool = False,
        proxy: Optional[str] = None,
    ) -> Optional[Union[Dict[str, Any], str]]:
        video = VideoCore(
            video_link, "", result_mode, timeout, get_upload_date, proxy=proxy
        )
        if get_upload_date:
            await video.html_create()
        await video.create()
        return video.result

    @staticmethod
    async def get_info(
        video_link: str,
        result_mode: int = ResultMode.dict,
        timeout: float = 2.0,
        proxy: Optional[str] = None,
    ) -> Optional[Union[Dict[str, Any], str]]:
        video = VideoCore(
            video_link, "getInfo", result_mode, timeout, True, proxy=proxy
        )
        await video.html_create()
        video.post_request_processing()
        return video.result

    @staticmethod
    async def get_formats(
        video_link: str,
        result_mode: int = ResultMode.dict,
        timeout: float = 2.0,
        proxy: Optional[str] = None,
    ) -> Optional[Union[Dict[str, Any], str]]:
        video = VideoCore(
            video_link, "getFormats", result_mode, timeout, False, proxy=proxy
        )
        await video.create()
        return video.result


class Suggestions:
    @staticmethod
    async def get(
        query: str,
        language: str = "en",
        region: str = "US",
        mode: int = ResultMode.dict,
        proxy: Optional[str] = None,
    ) -> Union[Dict[str, List[str]], str]:
        suggestions_internal = SuggestionsCore(
            language=language, region=region, proxy=proxy
        )
        return await suggestions_internal._get(query, mode)


class Playlist:
    playlistLink: str
    proxy: Optional[str]
    videos: List[Dict[str, Any]]
    info: Any
    hasMoreVideos: bool
    _playlist_core: Optional[PlaylistCore]

    def __init__(self, playlist_link: str, proxy: Optional[str] = None) -> None:
        self.playlistLink = playlist_link
        self.proxy = proxy
        self.videos = []
        self.info = None
        self.hasMoreVideos = True
        self._playlist_core = None

    async def get_next_videos(self) -> None:
        if not self.info:
            self._playlist_core = PlaylistCore(
                self.playlistLink, "", ResultMode.dict, 2.0, proxy=self.proxy
            )
            await self._playlist_core._next()
            self.info = copy.deepcopy(self._playlist_core.playlistComponent)
            self.videos = self._playlist_core.playlistComponent.get("videos", [])
            self.hasMoreVideos = self._playlist_core.continuationKey is not None
            if isinstance(self.info, dict):
                self.info.pop("videos", None)
        elif self._playlist_core:
            await self._playlist_core._next()
            self.videos = self._playlist_core.playlistComponent.get("videos", [])
            self.hasMoreVideos = self._playlist_core.continuationKey is not None

    @staticmethod
    async def get(
        playlist_link: str, proxy: Optional[str] = None
    ) -> Union[Dict[str, Any], str, None]:
        playlist = PlaylistCore(playlist_link, "", ResultMode.dict, 2.0, proxy=proxy)
        await playlist.create()
        return playlist.playlistComponent

    @staticmethod
    async def get_info(
        playlist_link: str, proxy: Optional[str] = None
    ) -> Union[Dict[str, Any], str, None]:
        playlist = PlaylistCore(
            playlist_link, "getInfo", ResultMode.dict, 2.0, proxy=proxy
        )
        await playlist.create()
        return playlist.playlistComponent

    @staticmethod
    async def get_videos(
        playlist_link: str, proxy: Optional[str] = None
    ) -> Union[Dict[str, Any], str, None]:
        playlist = PlaylistCore(
            playlist_link, "getVideos", ResultMode.dict, 2.0, proxy=proxy
        )
        await playlist.create()
        return playlist.playlistComponent


class Hashtag(HashtagCore):
    def __init__(
        self,
        hashtag: str,
        limit: int = 60,
        language: str = "en",
        region: str = "US",
        timeout: Optional[float] = None,
        proxy: Optional[str] = None,
    ) -> None:
        super().__init__(
            hashtag,
            limit,
            language,
            region,
            timeout if timeout is not None else 7.0,
            proxy=proxy,
        )

    async def next(self) -> bool:  # type: ignore[override]
        return await super().next()


class Transcript:
    @staticmethod
    async def get(
        video_link: str, params: Optional[str] = None, proxy: Optional[str] = None
    ) -> Dict[str, Any]:
        transcript_core = TranscriptCore(video_link, params, proxy=proxy)
        await transcript_core.create()
        return transcript_core.result


class Channel(ChannelCore):
    def __init__(
        self,
        channel_id: str,
        request_type: str = ChannelRequestType.playlists,
        proxy: Optional[str] = None,
    ) -> None:
        super().__init__(channel_id, request_type, proxy=proxy)

    async def init(self) -> None:
        await self.create()

    async def next(self) -> None:
        await super().next()

    @staticmethod
    async def get(
        channel_id: str,
        request_type: str = ChannelRequestType.playlists,
        proxy: Optional[str] = None,
    ) -> Dict[str, Any]:
        channel_core = ChannelCore(channel_id, request_type, proxy=proxy)
        await channel_core.create()
        return channel_core.result


class Recommendations:
    @staticmethod
    async def get_home(
        limit: int = 20,
        language: str = "en",
        region: str = "US",
        timeout: float = 20.0,
        proxy: Optional[str] = None,
    ) -> Dict[str, Any]:
        browse = BrowseCore(
            browse_id="FEwhat_to_watch",
            limit=limit,
            language=language,
            region=region,
            timeout=timeout,
            proxy=proxy,
        )
        return await browse.next()

    @staticmethod
    async def get_related(
        video_link: str,
        limit: int = 20,
        language: str = "en",
        region: str = "US",
        timeout: float = 20.0,
        proxy: Optional[str] = None,
    ) -> Dict[str, Any]:
        related = RelatedVideosCore(
            video_link=video_link,
            limit=limit,
            language=language,
            region=region,
            timeout=timeout,
            proxy=proxy,
        )
        return await related.next()
