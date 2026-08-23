import logging
from typing import Any, Dict, List, Optional, Union
from py_yt.core.componenthandler import getValue

from py_yt.core.constants import (
    videoElementKey,
    channelElementKey,
    playlistElementKey,
    shelfElementKey,
)

logger = logging.getLogger(__name__)


class ComponentHandler:
    def _getVideoComponent(
        self, element: dict, shelfTitle: Optional[str] = None
    ) -> dict:
        video = element[videoElementKey]
        vid = self._getValue(video, ["videoId"])
        component = {
            "type": "video",
            "id": vid,
            "title": self._getValue(video, ["title", "runs", 0, "text"]),
            "publishedTime": self._getValue(video, ["publishedTimeText", "simpleText"]),
            "duration": self._getValue(video, ["lengthText", "simpleText"]),
            "viewCount": {
                "text": self._getValue(video, ["viewCountText", "simpleText"]),
                "short": self._getValue(video, ["shortViewCountText", "simpleText"]),
            },
            "thumbnails": self._getValue(video, ["thumbnail", "thumbnails"]),
            "richThumbnail": self._getValue(
                video,
                [
                    "richThumbnail",
                    "movingThumbnailRenderer",
                    "movingThumbnailDetails",
                    "thumbnails",
                    0,
                ],
            ),
            "descriptionSnippet": self._getValue(
                video, ["detailedMetadataSnippets", 0, "snippetText", "runs"]
            ),
            "channel": {
                "name": self._getValue(video, ["ownerText", "runs", 0, "text"]),
                "id": self._getValue(
                    video,
                    [
                        "ownerText",
                        "runs",
                        0,
                        "navigationEndpoint",
                        "browseEndpoint",
                        "browseId",
                    ],
                ),
                "thumbnails": self._getValue(
                    video,
                    [
                        "channelThumbnailSupportedRenderers",
                        "channelThumbnailWithLinkRenderer",
                        "thumbnail",
                        "thumbnails",
                    ],
                ),
            },
            "accessibility": {
                "title": self._getValue(
                    video, ["title", "accessibility", "accessibilityData", "label"]
                ),
                "duration": self._getValue(
                    video, ["lengthText", "accessibility", "accessibilityData", "label"]
                ),
            },
        }
        component["link"] = "https://www.youtube.com/watch?v=" + vid if vid else None
        cid = component["channel"]["id"]
        if cid:
            component["channel"]["link"] = "https://www.youtube.com/channel/" + cid
        else:
            component["channel"]["link"] = None
        component["shelfTitle"] = shelfTitle
        return component

    def _getChannelComponent(self, element: dict) -> dict:
        channel = element[channelElementKey]
        cid = self._getValue(channel, ["channelId"])
        component = {
            "type": "channel",
            "id": cid,
            "title": self._getValue(channel, ["title", "simpleText"]),
            "thumbnails": self._getValue(channel, ["thumbnail", "thumbnails"]),
            "videoCount": self._getValue(
                channel, ["videoCountText", "runs", 0, "text"]
            ),
            "descriptionSnippet": self._getValue(
                channel, ["descriptionSnippet", "runs"]
            ),
            "subscribers": self._getValue(
                channel, ["subscriberCountText", "simpleText"]
            ),
        }
        component["link"] = "https://www.youtube.com/channel/" + cid if cid else None
        return component

    def _getPlaylistComponent(self, element: dict) -> dict:
        if playlistElementKey in element:
            playlist = element[playlistElementKey]
            component = {
                "type": "playlist",
                "id": self._getValue(playlist, ["playlistId"]),
                "title": self._getValue(playlist, ["title", "simpleText"]),
                "videoCount": self._getValue(playlist, ["videoCount"]),
                "channel": {
                    "name": self._getValue(
                        playlist, ["shortBylineText", "runs", 0, "text"]
                    ),
                    "id": self._getValue(
                        playlist,
                        [
                            "shortBylineText",
                            "runs",
                            0,
                            "navigationEndpoint",
                            "browseEndpoint",
                            "browseId",
                        ],
                    ),
                },
                "thumbnails": self._getValue(
                    playlist,
                    [
                        "thumbnailRenderer",
                        "playlistVideoThumbnailRenderer",
                        "thumbnail",
                        "thumbnails",
                    ],
                ),
            }
        elif "lockupViewModel" in element:
            lockup = element["lockupViewModel"]
            component = {
                "type": "playlist",
                "id": self._getValue(lockup, ["contentId"]),
                "title": self._getValue(
                    lockup,
                    ["metadata", "lockupMetadataViewModel", "title", "content"],
                ),
                "thumbnails": self._getValue(
                    lockup,
                    [
                        "contentImage",
                        "collectionThumbnailViewModel",
                        "primaryThumbnail",
                        "thumbnailViewModel",
                        "image",
                        "sources",
                    ],
                ),
                "videoCount": self._getValue(
                    lockup,
                    [
                        "contentImage",
                        "collectionThumbnailViewModel",
                        "primaryThumbnail",
                        "thumbnailViewModel",
                        "overlays",
                        0,
                        "thumbnailOverlayBadgeViewModel",
                        "thumbnailBadges",
                        0,
                        "thumbnailBadgeViewModel",
                        "text",
                    ],
                ),
                "channel": {
                    "name": self._getValue(
                        lockup,
                        [
                            "metadata",
                            "lockupMetadataViewModel",
                            "metadata",
                            "contentMetadataViewModel",
                            "metadataRows",
                            0,
                            "metadataParts",
                            0,
                            "text",
                            "content",
                        ],
                    ),
                    "id": self._getValue(
                        lockup,
                        [
                            "metadata",
                            "lockupMetadataViewModel",
                            "metadata",
                            "contentMetadataViewModel",
                            "metadataRows",
                            0,
                            "metadataParts",
                            0,
                            "text",
                            "commandRuns",
                            0,
                            "onTap",
                            "innertubeCommand",
                            "browseEndpoint",
                            "browseId",
                        ],
                    ),
                },
            }
        else:
            raise ValueError(
                "Unrecognized element format encountered in _getPlaylistComponent; "
                f"element keys: {list(element.keys())}"
            )

        pid = component["id"]
        component["link"] = (
            "https://www.youtube.com/playlist?list=" + pid if pid else None
        )
        cid = component["channel"]["id"]
        if cid:
            component["channel"]["link"] = "https://www.youtube.com/channel/" + cid
        else:
            component["channel"]["link"] = None
        return component

    def _getVideoFromChannelSearch(self, elements: Optional[list]) -> list:
        channelsearch: List[Dict[str, Any]] = []
        if not elements or not isinstance(elements, list):
            return channelsearch

        for element in elements:
            if not isinstance(element, dict):
                continue
            child = self._getValue(element, ["childVideoRenderer"])
            if not child:
                continue
            json_data = {
                "id": self._getValue(child, ["videoId"]),
                "title": self._getValue(child, ["title", "simpleText"]),
                "uri": self._getValue(
                    child,
                    [
                        "navigationEndpoint",
                        "commandMetadata",
                        "webCommandMetadata",
                        "url",
                    ],
                ),
                "duration": {
                    "simpleText": self._getValue(child, ["lengthText", "simpleText"]),
                    "text": self._getValue(
                        child,
                        ["lengthText", "accessibility", "accessibilityData", "label"],
                    ),
                },
            }
            channelsearch.append(json_data)
        return channelsearch

    def _getChannelSearchComponent(self, elements: list) -> list:
        channelsearch: List[Dict[str, Any]] = []
        if not elements or not isinstance(elements, list):
            return channelsearch

        for element in elements:
            if not isinstance(element, dict):
                continue

            responsetype = None

            if "gridPlaylistRenderer" in element:
                element = element["gridPlaylistRenderer"]
                responsetype = "gridplaylist"
            elif "itemSectionRenderer" in element:
                contents = element["itemSectionRenderer"].get("contents", [])
                if not contents:
                    continue
                first_content = contents[0]
                if "videoRenderer" in first_content:
                    element = first_content["videoRenderer"]
                    responsetype = "video"
                elif "playlistRenderer" in first_content:
                    element = first_content["playlistRenderer"]
                    responsetype = "playlist"
                else:
                    logger.debug(
                        "Skipping unrecognized itemSectionRenderer content: %s",
                        first_content,
                    )
                    continue
            elif "continuationItemRenderer" in element:
                continue
            else:
                logger.debug(
                    "Skipping unrecognized channel search element: %s", element
                )
                continue

            json_data: Dict[str, Any]
            if responsetype == "video":
                json_data = {
                    "id": self._getValue(element, ["videoId"]),
                    "thumbnails": {
                        "normal": self._getValue(element, ["thumbnail", "thumbnails"]),
                        "rich": self._getValue(
                            element,
                            [
                                "richThumbnail",
                                "movingThumbnailRenderer",
                                "movingThumbnailDetails",
                                "thumbnails",
                            ],
                        ),
                    },
                    "title": self._getValue(element, ["title", "runs", 0, "text"]),
                    "descriptionSnippet": self._getValue(
                        element, ["descriptionSnippet", "runs", 0, "text"]
                    ),
                    "uri": self._getValue(
                        element,
                        [
                            "navigationEndpoint",
                            "commandMetadata",
                            "webCommandMetadata",
                            "url",
                        ],
                    ),
                    "views": {
                        "precise": self._getValue(
                            element, ["viewCountText", "simpleText"]
                        ),
                        "simple": self._getValue(
                            element, ["shortViewCountText", "simpleText"]
                        ),
                        "approximate": self._getValue(
                            element,
                            [
                                "shortViewCountText",
                                "accessibility",
                                "accessibilityData",
                                "label",
                            ],
                        ),
                    },
                    "duration": {
                        "simpleText": self._getValue(
                            element, ["lengthText", "simpleText"]
                        ),
                        "text": self._getValue(
                            element,
                            [
                                "lengthText",
                                "accessibility",
                                "accessibilityData",
                                "label",
                            ],
                        ),
                    },
                    "published": self._getValue(
                        element, ["publishedTimeText", "simpleText"]
                    ),
                    "channel": {
                        "name": self._getValue(
                            element, ["ownerText", "runs", 0, "text"]
                        ),
                        "thumbnails": self._getValue(
                            element,
                            [
                                "channelThumbnailSupportedRenderers",
                                "channelThumbnailWithLinkRenderer",
                                "thumbnail",
                                "thumbnails",
                            ],
                        ),
                    },
                    "type": responsetype,
                }
            elif responsetype == "playlist":
                json_data = {
                    "id": self._getValue(element, ["playlistId"]),
                    "videos": self._getVideoFromChannelSearch(
                        self._getValue(element, ["videos"])
                    ),
                    "thumbnails": {
                        "normal": self._getValue(element, ["thumbnails"]),
                    },
                    "title": self._getValue(element, ["title", "simpleText"]),
                    "uri": self._getValue(
                        element,
                        [
                            "navigationEndpoint",
                            "commandMetadata",
                            "webCommandMetadata",
                            "url",
                        ],
                    ),
                    "channel": {
                        "name": self._getValue(
                            element, ["longBylineText", "runs", 0, "text"]
                        ),
                    },
                    "type": responsetype,
                }
            else:
                json_data = {
                    "id": self._getValue(element, ["playlistId"]),
                    "thumbnails": {
                        "normal": self._getValue(
                            element, ["thumbnail", "thumbnails", 0]
                        ),
                    },
                    "title": self._getValue(element, ["title", "runs", 0, "text"]),
                    "uri": self._getValue(
                        element,
                        [
                            "navigationEndpoint",
                            "commandMetadata",
                            "webCommandMetadata",
                            "url",
                        ],
                    ),
                    "type": "playlist",
                }
            channelsearch.append(json_data)
        return channelsearch

    def _getShelfComponent(self, element: dict) -> dict:
        shelf = element.get(shelfElementKey, {})
        return {
            "title": self._getValue(shelf, ["title", "simpleText"]),
            "elements": self._getValue(
                shelf, ["content", "verticalListRenderer", "items"]
            )
            or [],
        }

    def _getValue(self, source: Any, path: List[Union[str, int, None]]) -> Any:
        return getValue(source, path)
