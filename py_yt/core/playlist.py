import json
import logging
import re
from typing import Any, Dict, Iterable, List, Mapping, Optional, TypeVar, Union

from py_yt.core.componenthandler import get_value as core_get_value
from py_yt.core.constants import ResultMode, continuationKeyPath, playlistVideoKey
from py_yt.core.requests import RequestCore

logger = logging.getLogger(__name__)

K = TypeVar("K")
T = TypeVar("T")


class PlaylistCore(RequestCore):
    playlistComponent: Any = None
    result: Any = None
    continuationKey: Optional[str] = None
    responseSource: Optional[Dict[str, Any]] = None
    response: Optional[str] = None

    def __init__(
        self,
        playlist_link: str,
        componentMode: str,
        result_mode: int,
        timeout: float,
        proxy: Optional[str] = None,
    ) -> None:
        super().__init__(timeout=timeout, proxy=proxy)
        self.componentMode: str = componentMode
        self.resultMode: int = result_mode
        self.timeout: float = timeout
        self.url: str = playlist_link

    def post_processing(self) -> None:
        self._parse_source()
        self._get_components()
        if self.resultMode == ResultMode.json:
            self.result = json.dumps(self.playlistComponent, indent=4)
        else:
            self.result = self.playlistComponent

    async def create(self) -> None:
        status_code = await self._make_request()
        if status_code == 200:
            self.post_processing()
        else:
            raise Exception("ERROR: Invalid status code.")

    def next_post_processing(self) -> None:
        self._parse_source()
        self._get_next_components()
        if self.resultMode == ResultMode.json:
            self.result = json.dumps(self.playlistComponent, indent=4)
        else:
            self.result = self.playlistComponent

    async def _next(self) -> None:
        if self.continuationKey:
            self.prepare_next_request()
            response = await self.post_request()
            if response is None:
                raise Exception("ERROR: Could not make request.")
            self.response = await response.text()
            if response.status == 200:
                self.next_post_processing()
            else:
                raise Exception("ERROR: Invalid status code.")
        else:
            await self.create()

    def prepare_first_request(self) -> None:
        clean_url = (self.url or "").rstrip("/")

        match = re.search(r"(?<=list=)([a-zA-Z0-9+/=_-]+)", clean_url)
        _id = match.group() if match else clean_url

        if _id.startswith("RD"):
            # YouTube Mix Playlist
            video_id_match = re.search(r"(?<=v=)([a-zA-Z0-9_-]+)", clean_url)
            video_id = video_id_match.group() if video_id_match else None

            self.url = self._build_url("next")
            self.data = self._build_payload(
                playlistId=_id,
                videoId=video_id,
            )
        else:
            browseId = "VL" + _id if not _id.startswith("VL") else _id

            self.url = self._build_url("browse")
            self.data = self._build_payload(
                browseId=browseId,
            )

    async def _make_request(self) -> int:
        self.prepare_first_request()
        request = await self.post_request()
        if request is None:
            raise Exception("ERROR: Could not make request.")
        self.response = await request.text()
        return request.status

    def prepare_next_request(self) -> None:
        self.data = self._build_payload(
            continuation=self.continuationKey,
        )
        self.url = self._build_url("browse")

    def _parse_source(self) -> None:
        try:
            self.responseSource = json.loads(self.response or "{}")
        except Exception as e:
            logger.error("Could not parse YouTube playlist response", exc_info=True)
            raise Exception("ERROR: Could not parse YouTube response.") from e

    def _get_components(self) -> None:
        if isinstance(self.responseSource, dict) and "sidebar" in self.responseSource:
            # Traditional browse response
            sidebar = self.responseSource["sidebar"]["playlistSidebarRenderer"]["items"]
            inforenderer = sidebar[0]["playlistSidebarPrimaryInfoRenderer"]
            channel_details_available = len(sidebar) != 1
            channelrenderer = (
                sidebar[1]["playlistSidebarSecondaryInfoRenderer"]["videoOwner"][
                    "videoOwnerRenderer"
                ]
                if channel_details_available
                else None
            )
            videorenderer_val = self._get_first_value(
                self.responseSource,
                [
                    "contents",
                    "twoColumnBrowseResultsRenderer",
                    "tabs",
                    "tabRenderer",
                    "content",
                    "sectionListRenderer",
                    "contents",
                    "itemSectionRenderer",
                    "contents",
                    "playlistVideoListRenderer",
                    "contents",
                ],
            )
            videorenderer: List[Any] = (
                videorenderer_val if isinstance(videorenderer_val, list) else []
            )
            videos: List[Dict[str, Any]] = []
            for video in videorenderer:
                try:
                    video = video["playlistVideoRenderer"]
                    j = {
                        "id": self._get_value(video, ["videoId"]),
                        "thumbnails": self._get_value(
                            video, ["thumbnail", "thumbnails"]
                        ),
                        "title": self._get_value(video, ["title", "runs", 0, "text"]),
                        "channel": {
                            "name": self._get_value(
                                video, ["shortBylineText", "runs", 0, "text"]
                            ),
                            "id": self._get_value(
                                video,
                                [
                                    "shortBylineText",
                                    "runs",
                                    0,
                                    "navigationEndpoint",
                                    "browseEndpoint",
                                    "browseId",
                                ],
                            ),
                            "link": self._get_value(
                                video,
                                [
                                    "shortBylineText",
                                    "runs",
                                    0,
                                    "navigationEndpoint",
                                    "browseEndpoint",
                                    "canonicalBaseUrl",
                                ],
                            ),
                        },
                        "duration": self._get_value(
                            video, ["lengthText", "simpleText"]
                        ),
                        "accessibility": {
                            "title": self._get_value(
                                video,
                                [
                                    "title",
                                    "accessibility",
                                    "accessibilityData",
                                    "label",
                                ],
                            ),
                            "duration": self._get_value(
                                video,
                                [
                                    "lengthText",
                                    "accessibility",
                                    "accessibilityData",
                                    "label",
                                ],
                            ),
                        },
                        "link": "https://www.youtube.com"
                        + str(
                            self._get_value(
                                video,
                                [
                                    "navigationEndpoint",
                                    "commandMetadata",
                                    "webCommandMetadata",
                                    "url",
                                ],
                            )
                        ),
                        "isPlayable": self._get_value(video, ["isPlayable"]),
                    }
                    videos.append(j)
                except Exception:
                    pass

            playlistElement = {
                "info": {
                    "id": self._get_value(
                        inforenderer,
                        [
                            "title",
                            "runs",
                            0,
                            "navigationEndpoint",
                            "watchEndpoint",
                            "playlistId",
                        ],
                    ),
                    "thumbnails": self._get_value(
                        inforenderer,
                        [
                            "thumbnailRenderer",
                            "playlistVideoThumbnailRenderer",
                            "thumbnail",
                            "thumbnails",
                        ],
                    ),
                    "title": self._get_value(
                        inforenderer, ["title", "runs", 0, "text"]
                    ),
                    "videoCount": self._get_value(
                        inforenderer, ["stats", 0, "runs", 0, "text"]
                    ),
                    "viewCount": self._get_value(
                        inforenderer, ["stats", 1, "simpleText"]
                    ),
                    "link": self._get_value(
                        self.responseSource,
                        ["microformat", "microformatDataRenderer", "urlCanonical"],
                    ),
                    "channel": {
                        "id": (
                            self._get_value(
                                channelrenderer,
                                [
                                    "title",
                                    "runs",
                                    0,
                                    "navigationEndpoint",
                                    "browseEndpoint",
                                    "browseId",
                                ],
                            )
                            if channel_details_available
                            else None
                        ),
                        "name": (
                            self._get_value(
                                channelrenderer, ["title", "runs", 0, "text"]
                            )
                            if channel_details_available
                            else None
                        ),
                        "detailsAvailable": channel_details_available,
                        "link": (
                            "https://www.youtube.com"
                            + str(
                                self._get_value(
                                    channelrenderer,
                                    [
                                        "title",
                                        "runs",
                                        0,
                                        "navigationEndpoint",
                                        "browseEndpoint",
                                        "canonicalBaseUrl",
                                    ],
                                )
                            )
                            if channel_details_available
                            else None
                        ),
                        "thumbnails": (
                            self._get_value(
                                channelrenderer, ["thumbnail", "thumbnails"]
                            )
                            if channel_details_available
                            else None
                        ),
                    },
                },
                "videos": videos,
            }
            if self.componentMode == "getInfo":
                self.playlistComponent = playlistElement["info"]
            elif self.componentMode == "getVideos":
                self.playlistComponent = {"videos": videos}
            else:
                self.playlistComponent = playlistElement
            c_key = self._get_value(
                videorenderer,
                [
                    -1,
                    "continuationItemRenderer",
                    "continuationEndpoint",
                    "continuationCommand",
                    "token",
                ],
            )
            self.continuationKey = str(c_key) if c_key is not None else None
        elif (
            isinstance(self.responseSource, dict) and "contents" in self.responseSource
        ):
            # YouTube Mix Playlist (next endpoint)
            playlist = self.responseSource["contents"]["twoColumnWatchNextResults"][
                "playlist"
            ]["playlist"]
            videorenderer = playlist.get("contents", [])
            videos = []
            for video in videorenderer:
                try:
                    if "playlistPanelVideoRenderer" in video:
                        video = video["playlistPanelVideoRenderer"]
                        j = {
                            "id": self._get_value(video, ["videoId"]),
                            "thumbnails": self._get_value(
                                video, ["thumbnail", "thumbnails"]
                            ),
                            "title": self._get_value(video, ["title", "simpleText"])
                            or self._get_value(video, ["title", "runs", 0, "text"]),
                            "channel": {
                                "name": self._get_value(
                                    video, ["shortBylineText", "runs", 0, "text"]
                                ),
                                "id": self._get_value(
                                    video,
                                    [
                                        "shortBylineText",
                                        "runs",
                                        0,
                                        "navigationEndpoint",
                                        "browseEndpoint",
                                        "browseId",
                                    ],
                                ),
                                "link": "https://www.youtube.com"
                                + str(
                                    self._get_value(
                                        video,
                                        [
                                            "shortBylineText",
                                            "runs",
                                            0,
                                            "navigationEndpoint",
                                            "browseEndpoint",
                                            "canonicalBaseUrl",
                                        ],
                                    )
                                ),
                            },
                            "duration": self._get_value(
                                video, ["lengthText", "simpleText"]
                            ),
                            "link": "https://www.youtube.com/watch?v="
                            + str(self._get_value(video, ["videoId"])),
                        }
                        videos.append(j)
                except Exception:
                    pass
            playlistElement = {
                "info": {
                    "id": playlist.get("playlistId"),
                    "title": playlist.get("title"),
                    "videoCount": str(len(videos)),
                    "link": "https://www.youtube.com/playlist?list="
                    + str(playlist.get("playlistId")),
                    "channel": None,
                },
                "videos": videos,
            }
            if self.componentMode == "getInfo":
                self.playlistComponent = playlistElement["info"]
            elif self.componentMode == "getVideos":
                self.playlistComponent = {"videos": videos}
            else:
                self.playlistComponent = playlistElement
            self.continuationKey = None

    def _get_next_components(self) -> None:
        self.continuationKey = None
        playlistComponent: Dict[str, Any] = {
            "videos": [],
        }
        continuationElements = self._get_value(
            self.responseSource,
            [
                "onResponseReceivedActions",
                0,
                "appendContinuationItemsAction",
                "continuationItems",
            ],
        )
        if continuationElements is None or not isinstance(continuationElements, list):
            return
        for videoElement in continuationElements:
            if isinstance(videoElement, dict):
                if playlistVideoKey in videoElement:
                    videoComponent = {
                        "id": self._get_value(
                            videoElement, [playlistVideoKey, "videoId"]
                        ),
                        "title": self._get_value(
                            videoElement, [playlistVideoKey, "title", "runs", 0, "text"]
                        ),
                        "thumbnails": self._get_value(
                            videoElement, [playlistVideoKey, "thumbnail", "thumbnails"]
                        ),
                        "link": "https://www.youtube.com"
                        + str(
                            self._get_value(
                                videoElement,
                                [
                                    playlistVideoKey,
                                    "navigationEndpoint",
                                    "commandMetadata",
                                    "webCommandMetadata",
                                    "url",
                                ],
                            )
                        ),
                        "channel": {
                            "name": self._get_value(
                                videoElement,
                                [
                                    playlistVideoKey,
                                    "shortBylineText",
                                    "runs",
                                    0,
                                    "text",
                                ],
                            ),
                            "id": self._get_value(
                                videoElement,
                                [
                                    playlistVideoKey,
                                    "shortBylineText",
                                    "runs",
                                    0,
                                    "navigationEndpoint",
                                    "browseEndpoint",
                                    "browseId",
                                ],
                            ),
                            "link": "https://www.youtube.com"
                            + str(
                                self._get_value(
                                    videoElement,
                                    [
                                        playlistVideoKey,
                                        "shortBylineText",
                                        "runs",
                                        0,
                                        "navigationEndpoint",
                                        "browseEndpoint",
                                        "canonicalBaseUrl",
                                    ],
                                )
                            ),
                        },
                        "duration": self._get_value(
                            videoElement, [playlistVideoKey, "lengthText", "simpleText"]
                        ),
                        "accessibility": {
                            "title": self._get_value(
                                videoElement,
                                [
                                    playlistVideoKey,
                                    "title",
                                    "accessibility",
                                    "accessibilityData",
                                    "label",
                                ],
                            ),
                            "duration": self._get_value(
                                videoElement,
                                [
                                    playlistVideoKey,
                                    "lengthText",
                                    "accessibility",
                                    "accessibilityData",
                                    "label",
                                ],
                            ),
                        },
                    }
                    playlistComponent["videos"].append(videoComponent)
                c_key = self._get_value(videoElement, list(continuationKeyPath))
                self.continuationKey = str(c_key) if c_key is not None else None
        if (
            isinstance(self.playlistComponent, dict)
            and "videos" in self.playlistComponent
        ):
            self.playlistComponent["videos"].extend(playlistComponent["videos"])

    def _get_value(
        self, source: Any, path: Iterable[Union[str, int, None]]
    ) -> Any:
        return core_get_value(source, list(path))

    def _get_all_with_key(self, source: Iterable[Mapping[K, T]], key: K) -> Iterable[T]:
        if not isinstance(source, Iterable):
            return
        for item in source:
            if isinstance(item, Mapping) and key in item:
                yield item[key]

    def _get_value_ex(
        self, source: Any, path: List[Optional[str]]
    ) -> Iterable[Union[str, int, dict, None]]:
        if len(path) <= 0:
            yield source
            return
        key = path[0]
        upcoming = path[1:]
        if key is None:
            if not upcoming:
                yield None
                return
            following_key = upcoming[0]
            upcoming = upcoming[1:]
            if following_key is None:
                raise Exception(
                    "Cannot search for a key twice consecutive or at the end with no key given"
                )
            if isinstance(source, dict):
                for val in source.values():
                    if isinstance(val, dict) and following_key in val:
                        yield from self._get_value_ex(val[following_key], upcoming)
            elif isinstance(source, list):
                for item in source:
                    if isinstance(item, dict) and following_key in item:
                        yield from self._get_value_ex(item[following_key], upcoming)
        else:
            val = self._get_value(source, path=[key])
            yield from self._get_value_ex(val, path=upcoming)

    def _get_first_value(
        self, source: Any, path: Iterable[Optional[str]]
    ) -> Any:
        values = self._get_value_ex(source, list(path))
        for val in values:
            if val is not None:
                return val
        return None
