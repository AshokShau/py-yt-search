import logging
from typing import Any, Dict, List, Optional, Sequence, Union

from py_yt.core.componenthandler import (
    build_channel_url,
    build_playlist_url,
    build_watch_url,
    get_value,
)
from py_yt.core.constants import (
    channelElementKey,
    playlistElementKey,
    shelfElementKey,
    videoElementKey,
)

logger = logging.getLogger(__name__)


class ComponentHandler:
    def _get_video_component(
        self, element: Dict[str, Any], shelf_title: Optional[str] = None
    ) -> Dict[str, Any]:
        video = element[videoElementKey]
        vid: Optional[str] = self._get_value(video, ["videoId"])
        cid: Optional[str] = self._get_value(
            video,
            [
                "ownerText",
                "runs",
                0,
                "navigationEndpoint",
                "browseEndpoint",
                "browseId",
            ],
        )
        component: Dict[str, Any] = {
            "type": "video",
            "id": vid,
            "title": self._get_value(video, ["title", "runs", 0, "text"]),
            "publishedTime": self._get_value(video, ["publishedTimeText", "simpleText"]),
            "duration": self._get_value(video, ["lengthText", "simpleText"]),
            "viewCount": {
                "text": self._get_value(video, ["viewCountText", "simpleText"]),
                "short": self._get_value(video, ["shortViewCountText", "simpleText"]),
            },
            "thumbnails": self._get_value(video, ["thumbnail", "thumbnails"]),
            "richThumbnail": self._get_value(
                video,
                [
                    "richThumbnail",
                    "movingThumbnailRenderer",
                    "movingThumbnailDetails",
                    "thumbnails",
                    0,
                ],
            ),
            "descriptionSnippet": self._get_value(
                video, ["detailedMetadataSnippets", 0, "snippetText", "runs"]
            ),
            "channel": {
                "name": self._get_value(video, ["ownerText", "runs", 0, "text"]),
                "id": cid,
                "thumbnails": self._get_value(
                    video,
                    [
                        "channelThumbnailSupportedRenderers",
                        "channelThumbnailWithLinkRenderer",
                        "thumbnail",
                        "thumbnails",
                    ],
                ),
                "link": build_channel_url(cid),
            },
            "accessibility": {
                "title": self._get_value(
                    video, ["title", "accessibility", "accessibilityData", "label"]
                ),
                "duration": self._get_value(
                    video, ["lengthText", "accessibility", "accessibilityData", "label"]
                ),
            },
            "link": build_watch_url(vid),
            "shelfTitle": shelf_title,
        }
        return component

    def _get_channel_component(self, element: Dict[str, Any]) -> Dict[str, Any]:
        channel = element[channelElementKey]
        cid: Optional[str] = self._get_value(channel, ["channelId"])
        component: Dict[str, Any] = {
            "type": "channel",
            "id": cid,
            "title": self._get_value(channel, ["title", "simpleText"]),
            "thumbnails": self._get_value(channel, ["thumbnail", "thumbnails"]),
            "videoCount": self._get_value(
                channel, ["videoCountText", "runs", 0, "text"]
            ),
            "descriptionSnippet": self._get_value(
                channel, ["descriptionSnippet", "runs"]
            ),
            "subscribers": self._get_value(
                channel, ["subscriberCountText", "simpleText"]
            ),
            "link": build_channel_url(cid),
        }
        return component

    def _get_playlist_component(self, element: Dict[str, Any]) -> Dict[str, Any]:
        if playlistElementKey in element:
            playlist = element[playlistElementKey]
            component: Dict[str, Any] = {
                "type": "playlist",
                "id": self._get_value(playlist, ["playlistId"]),
                "title": self._get_value(playlist, ["title", "simpleText"]),
                "videoCount": self._get_value(playlist, ["videoCount"]),
                "channel": {
                    "name": self._get_value(
                        playlist, ["shortBylineText", "runs", 0, "text"]
                    ),
                    "id": self._get_value(
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
                "thumbnails": self._get_value(
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
                "id": self._get_value(lockup, ["contentId"]),
                "title": self._get_value(
                    lockup,
                    ["metadata", "lockupMetadataViewModel", "title", "content"],
                ),
                "thumbnails": self._get_value(
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
                "videoCount": self._get_value(
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
                    "name": self._get_value(
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
                    "id": self._get_value(
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
                "Unrecognized element format encountered in _get_playlist_component; "
                f"element keys: {list(element.keys())}"
            )

        pid: Optional[str] = component["id"]
        cid: Optional[str] = component["channel"]["id"]
        component["link"] = build_playlist_url(pid)
        component["channel"]["link"] = build_channel_url(cid)
        return component

    def _get_video_from_channel_search(
        self, elements: Optional[List[Any]]
    ) -> List[Dict[str, Any]]:
        channelsearch: List[Dict[str, Any]] = []
        if not elements or not isinstance(elements, list):
            return channelsearch

        for element in elements:
            if not isinstance(element, dict):
                continue
            child = self._get_value(element, ["childVideoRenderer"])
            if not child:
                continue
            json_data = {
                "id": self._get_value(child, ["videoId"]),
                "title": self._get_value(child, ["title", "simpleText"]),
                "uri": self._get_value(
                    child,
                    [
                        "navigationEndpoint",
                        "commandMetadata",
                        "webCommandMetadata",
                        "url",
                    ],
                ),
                "duration": {
                    "simpleText": self._get_value(child, ["lengthText", "simpleText"]),
                    "text": self._get_value(
                        child,
                        ["lengthText", "accessibility", "accessibilityData", "label"],
                    ),
                },
            }
            channelsearch.append(json_data)
        return channelsearch

    def _get_channel_search_component(
        self, elements: List[Any]
    ) -> List[Dict[str, Any]]:
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
                    "id": self._get_value(element, ["videoId"]),
                    "thumbnails": {
                        "normal": self._get_value(element, ["thumbnail", "thumbnails"]),
                        "rich": self._get_value(
                            element,
                            [
                                "richThumbnail",
                                "movingThumbnailRenderer",
                                "movingThumbnailDetails",
                                "thumbnails",
                            ],
                        ),
                    },
                    "title": self._get_value(element, ["title", "runs", 0, "text"]),
                    "descriptionSnippet": self._get_value(
                        element, ["descriptionSnippet", "runs", 0, "text"]
                    ),
                    "uri": self._get_value(
                        element,
                        [
                            "navigationEndpoint",
                            "commandMetadata",
                            "webCommandMetadata",
                            "url",
                        ],
                    ),
                    "views": {
                        "precise": self._get_value(
                            element, ["viewCountText", "simpleText"]
                        ),
                        "simple": self._get_value(
                            element, ["shortViewCountText", "simpleText"]
                        ),
                        "approximate": self._get_value(
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
                        "simpleText": self._get_value(
                            element, ["lengthText", "simpleText"]
                        ),
                        "text": self._get_value(
                            element,
                            [
                                "lengthText",
                                "accessibility",
                                "accessibilityData",
                                "label",
                            ],
                        ),
                    },
                    "published": self._get_value(
                        element, ["publishedTimeText", "simpleText"]
                    ),
                    "channel": {
                        "name": self._get_value(
                            element, ["ownerText", "runs", 0, "text"]
                        ),
                        "thumbnails": self._get_value(
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
                    "id": self._get_value(element, ["playlistId"]),
                    "videos": self._get_video_from_channel_search(
                        self._get_value(element, ["videos"])
                    ),
                    "thumbnails": {
                        "normal": self._get_value(element, ["thumbnails"]),
                    },
                    "title": self._get_value(element, ["title", "simpleText"]),
                    "uri": self._get_value(
                        element,
                        [
                            "navigationEndpoint",
                            "commandMetadata",
                            "webCommandMetadata",
                            "url",
                        ],
                    ),
                    "channel": {
                        "name": self._get_value(
                            element, ["longBylineText", "runs", 0, "text"]
                        ),
                    },
                    "type": responsetype,
                }
            else:
                json_data = {
                    "id": self._get_value(element, ["playlistId"]),
                    "thumbnails": {
                        "normal": self._get_value(
                            element, ["thumbnail", "thumbnails", 0]
                        ),
                    },
                    "title": self._get_value(element, ["title", "runs", 0, "text"]),
                    "uri": self._get_value(
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

    def _get_shelf_component(self, element: Dict[str, Any]) -> Dict[str, Any]:
        shelf = element.get(shelfElementKey, {})
        return {
            "title": self._get_value(shelf, ["title", "simpleText"]),
            "elements": self._get_value(
                shelf, ["content", "verticalListRenderer", "items"]
            )
            or [],
        }

    def _get_value(self, source: Any, path: Sequence[Union[str, int, None]]) -> Any:
        return get_value(source, path)
