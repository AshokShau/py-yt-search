import copy
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from py_yt.core.componenthandler import getValue
from py_yt.core.constants import searchKey, requestPayload
from py_yt.core.requests import RequestCore

logger = logging.getLogger(__name__)


class ChannelCore(RequestCore):
    def __init__(self, channel_id: str, request_params: str, proxy: str | None = None):
        super().__init__(proxy=proxy)
        self.browseId = channel_id
        self.params = request_params
        self.result: Dict[str, Any] = {}
        self.continuation: Optional[str] = None
        self.responseSource: Optional[Any] = None

    def prepare_request(self):
        self.url = (
            "https://www.youtube.com/youtubei/v1/browse"
            + "?"
            + urlencode({"key": searchKey, "prettyPrint": "false"})
        )
        self.data = copy.deepcopy(requestPayload)
        if not self.continuation:
            self.data["params"] = self.params
            self.data["browseId"] = self.browseId
        else:
            self.data["continuation"] = self.continuation

    def playlist_parse(self, i: dict) -> dict:
        return {
            "id": getValue(i, ["playlistId"]),
            "thumbnails": getValue(i, ["thumbnail", "thumbnails"]),
            "title": getValue(i, ["title", "runs", 0, "text"]),
            "videoCount": getValue(i, ["videoCountShortText", "simpleText"]),
            "lastEdited": getValue(i, ["publishedTimeText", "simpleText"]),
        }

    async def parse_response(self):
        response = self.responseSource
        if not isinstance(response, dict):
            self.result = {}
            return

        thumbnails: List[Any] = []
        avatar_header = getValue(
            response, ["header", "c4TabbedHeaderRenderer", "avatar", "thumbnails"]
        )
        if avatar_header and isinstance(avatar_header, list):
            thumbnails.extend(avatar_header)

        avatar_meta = getValue(
            response, ["metadata", "channelMetadataRenderer", "avatar", "thumbnails"]
        )
        if avatar_meta and isinstance(avatar_meta, list):
            thumbnails.extend(avatar_meta)

        avatar_micro = getValue(
            response,
            ["microformat", "microformatDataRenderer", "thumbnail", "thumbnails"],
        )
        if avatar_micro and isinstance(avatar_micro, list):
            thumbnails.extend(avatar_micro)

        tabData: dict = {}
        playlists: List[dict] = []

        tabs = getValue(
            response, ["contents", "twoColumnBrowseResultsRenderer", "tabs"]
        )
        if tabs and isinstance(tabs, list):
            for tab in tabs:
                if not isinstance(tab, dict):
                    continue
                title = getValue(tab, ["tabRenderer", "title"])
                if title == "Playlists":
                    playlist_items = getValue(
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
                            if getValue(item, ["continuationItemRenderer"]):
                                self.continuation = getValue(
                                    item,
                                    [
                                        "continuationItemRenderer",
                                        "continuationEndpoint",
                                        "continuationCommand",
                                        "token",
                                    ],
                                )
                                break
                            pl_data = getValue(item, ["gridPlaylistRenderer"])
                            if pl_data and isinstance(pl_data, dict):
                                playlists.append(self.playlist_parse(pl_data))
                elif title == "About":
                    tabData = tab.get("tabRenderer", {})

        metadata = getValue(
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
            metadata = getValue(
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
            "id": getValue(
                response, ["metadata", "channelMetadataRenderer", "externalId"]
            ),
            "url": getValue(
                response, ["metadata", "channelMetadataRenderer", "channelUrl"]
            ),
            "description": getValue(
                response, ["metadata", "channelMetadataRenderer", "description"]
            ),
            "title": getValue(
                response, ["metadata", "channelMetadataRenderer", "title"]
            ),
            "banners": getValue(
                response, ["header", "c4TabbedHeaderRenderer", "banner", "thumbnails"]
            ),
            "subscribers": {
                "simpleText": getValue(
                    response,
                    [
                        "header",
                        "c4TabbedHeaderRenderer",
                        "subscriberCountText",
                        "simpleText",
                    ],
                ),
                "label": getValue(
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
            "availableCountryCodes": getValue(
                response,
                ["metadata", "channelMetadataRenderer", "availableCountryCodes"],
            ),
            "isFamilySafe": getValue(
                response, ["metadata", "channelMetadataRenderer", "isFamilySafe"]
            ),
            "keywords": getValue(
                response, ["metadata", "channelMetadataRenderer", "keywords"]
            ),
            "tags": getValue(
                response, ["microformat", "microformatDataRenderer", "tags"]
            ),
            "views": (
                getValue(metadata, ["viewCountText", "simpleText"])
                or getValue(metadata, ["viewCount"])
                if metadata
                else None
            ),
            "joinedDate": (
                getValue(metadata, ["joinedDateText", "runs", -1, "text"])
                or getValue(metadata, ["joinedDateText"])
                if metadata
                else None
            ),
            "country": (
                getValue(metadata, ["country", "simpleText"]) if metadata else None
            ),
            "playlists": playlists,
        }

    async def parse_next_response(self):
        if not isinstance(self.responseSource, dict):
            return

        self.continuation = None

        items = getValue(
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
            if getValue(i, ["continuationItemRenderer"]):
                self.continuation = getValue(
                    i,
                    [
                        "continuationItemRenderer",
                        "continuationEndpoint",
                        "continuationCommand",
                        "token",
                    ],
                )
                break
            elif getValue(i, ["gridPlaylistRenderer"]):
                grid_pl = getValue(i, ["gridPlaylistRenderer"])
                if grid_pl and isinstance(grid_pl, dict):
                    self.result.setdefault("playlists", []).append(
                        self.playlist_parse(grid_pl)
                    )

    async def next(self):
        if not self.continuation:
            return
        self.prepare_request()
        resp = await self.postRequest()
        if resp is None:
            raise Exception("ERROR: Could not make request.")
        self.responseSource = await resp.json()
        await self.parse_next_response()

    def has_more_playlists(self):
        return self.continuation is not None

    async def create(self):
        self.prepare_request()
        resp = await self.postRequest()
        if resp is None:
            raise Exception("ERROR: Could not make request.")
        self.responseSource = await resp.json()
        await self.parse_response()
