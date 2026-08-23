import logging
from typing import Any, Dict, List, Optional

from py_yt.core.componenthandler import get_value
from py_yt.core.requests import RequestCore

logger = logging.getLogger(__name__)


class ChannelCore(RequestCore):
    def __init__(
        self, channel_id: str, request_params: str, proxy: Optional[str] = None
    ) -> None:
        super().__init__(proxy=proxy)
        self.browseId: str = channel_id
        self.params: str = request_params
        self.result: Dict[str, Any] = {}
        self.continuation: Optional[str] = None
        self.responseSource: Optional[Dict[str, Any]] = None

    def prepare_request(self) -> None:
        self.url = self._build_url("browse", {"prettyPrint": "false"})
        if not self.continuation:
            self.data = self._build_payload(
                params=self.params,
                browseId=self.browseId,
            )
        else:
            self.data = self._build_payload(
                continuation=self.continuation,
            )

    def playlist_parse(self, i: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": get_value(i, ["playlistId"]),
            "thumbnails": get_value(i, ["thumbnail", "thumbnails"]),
            "title": get_value(i, ["title", "runs", 0, "text"]),
            "videoCount": get_value(i, ["videoCountShortText", "simpleText"]),
            "lastEdited": get_value(i, ["publishedTimeText", "simpleText"]),
        }

    async def parse_response(self) -> None:
        response = self.responseSource
        if not isinstance(response, dict):
            self.result = {}
            return

        thumbnails: List[Any] = []
        avatar_header = get_value(
            response, ["header", "c4TabbedHeaderRenderer", "avatar", "thumbnails"]
        )
        if avatar_header and isinstance(avatar_header, list):
            thumbnails.extend(avatar_header)

        avatar_meta = get_value(
            response, ["metadata", "channelMetadataRenderer", "avatar", "thumbnails"]
        )
        if avatar_meta and isinstance(avatar_meta, list):
            thumbnails.extend(avatar_meta)

        avatar_micro = get_value(
            response,
            ["microformat", "microformatDataRenderer", "thumbnail", "thumbnails"],
        )
        if avatar_micro and isinstance(avatar_micro, list):
            thumbnails.extend(avatar_micro)

        tabData: Dict[str, Any] = {}
        playlists: List[Dict[str, Any]] = []

        tabs = get_value(
            response, ["contents", "twoColumnBrowseResultsRenderer", "tabs"]
        )
        if tabs and isinstance(tabs, list):
            for tab in tabs:
                if not isinstance(tab, dict):
                    continue
                title = get_value(tab, ["tabRenderer", "title"])
                if title == "Playlists":
                    playlist_items = get_value(
                        tab,
                        [
                            "tabRenderer",
                            "content",
                            "sectionListRenderer",
                            "contents",
                            0,
                            "itemSectionRenderer",
                            "contents",
                            0,
                            "gridRenderer",
                            "items",
                        ],
                    )
                    if playlist_items and isinstance(playlist_items, list):
                        for item in playlist_items:
                            if not isinstance(item, dict):
                                continue
                            if get_value(item, ["continuationItemRenderer"]):
                                self.continuation = get_value(
                                    item,
                                    [
                                        "continuationItemRenderer",
                                        "continuationEndpoint",
                                        "continuationCommand",
                                        "token",
                                    ],
                                )
                                break
                            pl_data = get_value(item, ["gridPlaylistRenderer"])
                            if pl_data and isinstance(pl_data, dict):
                                playlists.append(self.playlist_parse(pl_data))
                elif title == "About":
                    tabData = tab.get("tabRenderer", {})

        metadata = get_value(
            tabData,
            [
                "content",
                "sectionListRenderer",
                "contents",
                0,
                "itemSectionRenderer",
                "contents",
                0,
                "channelAboutFullMetadataRenderer",
            ],
        )
        if not metadata:
            # Fallback for new About tab structure
            metadata = get_value(
                tabData,
                [
                    "content",
                    "sectionListRenderer",
                    "contents",
                    0,
                    "itemSectionRenderer",
                    "contents",
                    0,
                    "aboutChannelRenderer",
                    "metadata",
                    "aboutChannelMetadataViewModel",
                ],
            )

        self.result = {
            "id": get_value(
                response, ["metadata", "channelMetadataRenderer", "externalId"]
            ),
            "url": get_value(
                response, ["metadata", "channelMetadataRenderer", "channelUrl"]
            ),
            "description": get_value(
                response, ["metadata", "channelMetadataRenderer", "description"]
            ),
            "title": get_value(
                response, ["metadata", "channelMetadataRenderer", "title"]
            ),
            "banners": get_value(
                response, ["header", "c4TabbedHeaderRenderer", "banner", "thumbnails"]
            ),
            "subscribers": {
                "simpleText": get_value(
                    response,
                    [
                        "header",
                        "c4TabbedHeaderRenderer",
                        "subscriberCountText",
                        "simpleText",
                    ],
                ),
                "label": get_value(
                    response,
                    [
                        "header",
                        "c4TabbedHeaderRenderer",
                        "subscriberCountText",
                        "accessibility",
                        "accessibilityData",
                        "label",
                    ],
                ),
            },
            "thumbnails": thumbnails,
            "availableCountryCodes": get_value(
                response,
                ["metadata", "channelMetadataRenderer", "availableCountryCodes"],
            ),
            "isFamilySafe": get_value(
                response, ["metadata", "channelMetadataRenderer", "isFamilySafe"]
            ),
            "keywords": get_value(
                response, ["metadata", "channelMetadataRenderer", "keywords"]
            ),
            "tags": get_value(
                response, ["microformat", "microformatDataRenderer", "tags"]
            ),
            "views": (
                get_value(metadata, ["viewCountText", "simpleText"])
                or get_value(metadata, ["viewCount"])
                if metadata
                else None
            ),
            "joinedDate": (
                get_value(metadata, ["joinedDateText", "runs", -1, "text"])
                or get_value(metadata, ["joinedDateText"])
                if metadata
                else None
            ),
            "country": (
                get_value(metadata, ["country", "simpleText"]) if metadata else None
            ),
            "playlists": playlists,
        }

    async def parse_next_response(self) -> None:
        if not isinstance(self.responseSource, dict):
            return

        self.continuation = None

        items = get_value(
            self.responseSource,
            [
                "onResponseReceivedActions",
                0,
                "appendContinuationItemsAction",
                "continuationItems",
            ],
        )
        if not items or not isinstance(items, list):
            return

        for i in items:
            if not isinstance(i, dict):
                continue
            if get_value(i, ["continuationItemRenderer"]):
                self.continuation = get_value(
                    i,
                    [
                        "continuationItemRenderer",
                        "continuationEndpoint",
                        "continuationCommand",
                        "token",
                    ],
                )
                break
            elif get_value(i, ["gridPlaylistRenderer"]):
                grid_pl = get_value(i, ["gridPlaylistRenderer"])
                if grid_pl and isinstance(grid_pl, dict):
                    self.result.setdefault("playlists", []).append(
                        self.playlist_parse(grid_pl)
                    )

    async def next(self) -> None:
        if not self.continuation:
            return
        self.prepare_request()
        resp = await self.post_request()
        if resp is None:
            raise Exception("ERROR: Could not make request.")
        self.responseSource = await resp.json()
        await self.parse_next_response()

    def has_more_playlists(self) -> bool:
        return self.continuation is not None

    async def create(self) -> None:
        self.prepare_request()
        resp = await self.post_request()
        if resp is None:
            raise Exception("ERROR: Could not make request.")
        self.responseSource = await resp.json()
        await self.parse_response()
