import copy
from typing import Union

from py_yt.core.browse import BrowseCore
from py_yt.core.channel import ChannelCore
from py_yt.core.constants import ResultMode, ChannelRequestType
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
        timeout: int = 2,
        get_upload_date: bool = False,
        proxy: str | None = None,
    ) -> Union[dict, None]:
        video = VideoCore(
            video_link, None, result_mode, timeout, get_upload_date, proxy=proxy
        )
        if get_upload_date:
            await video.html_create()
        await video.create()
        return video.result

    @staticmethod
    async def getInfo(
        video_link: str,
        result_mode: int = ResultMode.dict,
        timeout: int = 2,
        proxy: str | None = None,
    ) -> Union[dict, None]:
        video = VideoCore(video_link, "getInfo", result_mode, timeout, True, proxy=proxy)
        await video.html_create()
        video.post_request_processing()
        return video.result

    @staticmethod
    async def getFormats(
        video_link: str,
        result_mode: int = ResultMode.dict,
        timeout: int = 2,
        proxy: str | None = None,
    ) -> Union[dict, None]:
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
        proxy: str | None = None,
    ):
        suggestionsInternal = SuggestionsCore(
            language=language, region=region, proxy=proxy
        )
        suggestions = await suggestionsInternal._get(query, mode)
        return suggestions


class Playlist:
    playlistLink = None
    videos = []
    info = None
    hasMoreVideos = True
    __playlist = None

    def __init__(self, playlistLink: str, proxy: str | None = None):
        self.playlistLink = playlistLink
        self.proxy = proxy

    async def getNextVideos(self) -> None:
        if not self.info:
            self.__playlist = PlaylistCore(
                self.playlistLink, None, ResultMode.dict, 2, proxy=self.proxy
            )
            await self.__playlist._next()
            self.info = copy.deepcopy(self.__playlist.playlistComponent)
            self.videos = self.__playlist.playlistComponent["videos"]
            self.hasMoreVideos = self.__playlist.continuationKey != None
            self.info.pop("videos")
        else:
            await self.__playlist._next()
            self.videos = self.__playlist.playlistComponent["videos"]
            self.hasMoreVideos = self.__playlist.continuationKey != None

    @staticmethod
    async def get(
        playlistLink: str, proxy: str | None = None
    ) -> Union[dict, str, None]:
        playlist = PlaylistCore(playlistLink, None, ResultMode.dict, 2, proxy=proxy)
        await playlist.create()
        return playlist.playlistComponent

    @staticmethod
    async def getInfo(
        playlistLink: str, proxy: str | None = None
    ) -> Union[dict, str, None]:
        playlist = PlaylistCore(
            playlistLink, "getInfo", ResultMode.dict, 2, proxy=proxy
        )
        await playlist.create()
        return playlist.playlistComponent

    @staticmethod
    async def getVideos(
        playlistLink: str, proxy: str | None = None
    ) -> Union[dict, str, None]:
        playlist = PlaylistCore(
            playlistLink, "getVideos", ResultMode.dict, 2, proxy=proxy
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
        timeout: int = None,
        proxy: str | None = None,
    ):
        super().__init__(hashtag, limit, language, region, timeout, proxy=proxy)

    async def next(self) -> dict:
        self.response = None
        self.resultComponents = []
        if self.params is None:
            await self._getParams()
        await self._makeRequest()
        self._getComponents()
        return {
            "result": self.resultComponents,
        }


class Transcript:
    @staticmethod
    async def get(videoLink: str, params: str = None, proxy: str | None = None):
        transcript_core = TranscriptCore(videoLink, params, proxy=proxy)
        await transcript_core.create()
        return transcript_core.result


class Channel(ChannelCore):
    def __init__(
        self,
        channel_id: str,
        request_type: str = ChannelRequestType.playlists,
        proxy: str | None = None,
    ):
        super().__init__(channel_id, request_type, proxy=proxy)

    async def init(self):
        await self.create()

    async def next(self):
        await super().next()

    @staticmethod
    async def get(
        channel_id: str,
        request_type: str = ChannelRequestType.playlists,
        proxy: str | None = None,
    ):
        channel_core = ChannelCore(channel_id, request_type, proxy=proxy)
        await channel_core.create()
        return channel_core.result


class Recommendations:
    @staticmethod
    async def getHome(
        limit: int = 20,
        language: str = "en",
        region: str = "US",
        timeout: int = 20,
        proxy: str | None = None,
    ) -> dict:
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
    async def getRelated(
        video_link: str,
        limit: int = 20,
        language: str = "en",
        region: str = "US",
        timeout: int = 20,
        proxy: str | None = None,
    ) -> dict:
        related = RelatedVideosCore(
            video_link=video_link,
            limit=limit,
            language=language,
            region=region,
            timeout=timeout,
            proxy=proxy,
        )
        return await related.next()
