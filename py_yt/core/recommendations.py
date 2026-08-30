from typing import Any, Dict, List, Optional

from py_yt.core.componenthandler import (
    build_channel_url,
    build_playlist_url,
    build_watch_url,
    get_video_id,
)
from py_yt.core.requests import RequestCore
from py_yt.handlers.componenthandler import ComponentHandler


class RelatedVideosCore(RequestCore, ComponentHandler):
    responseSource: Optional[Dict[str, Any]] = None

    def __init__(
        self,
        video_link: str,
        limit: int = 20,
        language: str = "en",
        region: str = "US",
        timeout: float = 20.0,
        max_retries: int = 0,
        proxy: Optional[str] = None,
    ) -> None:
        super().__init__(timeout=timeout, max_retries=max_retries, proxy=proxy)
        self.video_link: str = video_link
        self.limit: int = limit
        self.language: str = language
        self.region: str = region
        self.continuationKey: Optional[str] = None
        self.resultComponents: List[Dict[str, Any]] = []

    def _get_request_body(self) -> None:
        self.url = self._build_url("next")
        self.data = self._build_payload(
            language=self.language,
            region=self.region,
            client_name="MWEB",
            client_version="2.20260821.00.00",
            videoId=get_video_id(self.video_link),
            continuation=self.continuationKey,
        )

    async def _make_request(self) -> None:
        self._get_request_body()
        response = await self.post_request()
        if response:
            self.responseSource = await response.json()
        else:
            raise Exception("ERROR: Could not make request.")

    async def next(self) -> Dict[str, Any]:
        self.resultComponents = []
        await self._make_request()
        self._parse_source()
        return {
            "result": self.resultComponents,
        }

    def _parse_source(self) -> None:
        if not self.responseSource:
            return

        contents: List[Any] = []
        if not self.continuationKey:
            secondary_results = self._get_value(
                self.responseSource,
                [
                    "contents",
                    "twoColumnWatchNextResults",
                    "secondaryResults",
                    "secondaryResults",
                    "results",
                ],
            )
            if not secondary_results:
                secondary_results = self._get_value(
                    self.responseSource,
                    [
                        "contents",
                        "singleColumnWatchNextResults",
                        "pivot",
                        "pivotRenderer",
                        "contents",
                    ],
                )

            if not secondary_results:
                secondary_results = self._get_value(
                    self.responseSource,
                    [
                        "contents",
                        "singleColumnWatchNextResults",
                        "results",
                        "results",
                        "contents",
                    ],
                )

            if secondary_results and isinstance(secondary_results, list):
                contents = secondary_results
        else:
            continuation_actions = self._get_value(
                self.responseSource, ["onResponseReceivedEndpoints"]
            )
            if continuation_actions and isinstance(continuation_actions, list):
                for action in continuation_actions:
                    if (
                        isinstance(action, dict)
                        and "appendContinuationItemsAction" in action
                    ):
                        items = action["appendContinuationItemsAction"].get(
                            "continuationItems", []
                        )
                        if isinstance(items, list):
                            contents.extend(items)

        if not contents:
            return

        for element in contents:
            if not isinstance(element, dict):
                continue
            if "compactVideoRenderer" in element:
                self.resultComponents.append(self._get_compact_video_component(element))
            elif "videoWithContextRenderer" in element:
                self.resultComponents.append(
                    self._get_video_with_context_component(element)
                )
            elif "compactPlaylistRenderer" in element:
                self.resultComponents.append(self._get_compact_playlist_component(element))
            elif "itemSectionRenderer" in element:
                nested_contents = self._get_value(
                    element, ["itemSectionRenderer", "contents"]
                )
                if nested_contents and isinstance(nested_contents, list):
                    for nested in nested_contents:
                        if not isinstance(nested, dict):
                            continue
                        if len(self.resultComponents) >= self.limit:
                            break
                        if "compactVideoRenderer" in nested:
                            self.resultComponents.append(
                                self._get_compact_video_component(nested)
                            )
                        elif "videoWithContextRenderer" in nested:
                            self.resultComponents.append(
                                self._get_video_with_context_component(nested)
                            )
            elif "continuationItemRenderer" in element:
                token = self._get_value(
                    element,
                    [
                        "continuationItemRenderer",
                        "continuationEndpoint",
                        "continuationCommand",
                        "token",
                    ],
                )
                self.continuationKey = str(token) if token else None

            if len(self.resultComponents) >= self.limit:
                break

    def _get_compact_video_component(self, element: Dict[str, Any]) -> Dict[str, Any]:
        video = element["compactVideoRenderer"]
        vid: Optional[str] = self._get_value(video, ["videoId"])
        cid: Optional[str] = self._get_value(
            video,
            [
                "shortBylineText",
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
            "title": self._get_value(video, ["title", "simpleText"]),
            "publishedTime": self._get_value(video, ["publishedTimeText", "simpleText"]),
            "duration": self._get_value(video, ["lengthText", "simpleText"]),
            "viewCount": {
                "text": self._get_value(video, ["viewCountText", "simpleText"]),
                "short": self._get_value(video, ["shortViewCountText", "simpleText"]),
            },
            "thumbnails": self._get_value(video, ["thumbnail", "thumbnails"]),
            "channel": {
                "name": self._get_value(video, ["shortBylineText", "runs", 0, "text"]),
                "id": cid,
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
        }
        return component

    def _get_video_with_context_component(self, element: Dict[str, Any]) -> Dict[str, Any]:
        video = element["videoWithContextRenderer"]
        vid: Optional[str] = self._get_value(video, ["videoId"])
        cid: Optional[str] = self._get_value(
            video,
            [
                "shortBylineText",
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
            "title": self._get_value(video, ["headline", "runs", 0, "text"]),
            "publishedTime": self._get_value(
                video, ["publishedTimeText", "runs", 0, "text"]
            ),
            "duration": self._get_value(video, ["lengthText", "runs", 0, "text"]),
            "viewCount": {
                "text": self._get_value(
                    video, ["shortViewCountText", "runs", 0, "text"]
                ),
                "short": self._get_value(
                    video, ["shortViewCountText", "runs", 0, "text"]
                ),
            },
            "thumbnails": self._get_value(video, ["thumbnail", "thumbnails"]),
            "channel": {
                "name": self._get_value(video, ["shortBylineText", "runs", 0, "text"]),
                "id": cid,
                "link": build_channel_url(cid),
            },
            "accessibility": {
                "title": self._get_value(
                    video, ["headline", "accessibility", "accessibilityData", "label"]
                ),
                "duration": self._get_value(
                    video, ["lengthText", "accessibility", "accessibilityData", "label"]
                ),
            },
            "link": build_watch_url(vid),
        }
        return component

    def _get_compact_playlist_component(self, element: Dict[str, Any]) -> Dict[str, Any]:
        playlist = element["compactPlaylistRenderer"]
        pid: Optional[str] = self._get_value(playlist, ["playlistId"])
        cid: Optional[str] = self._get_value(
            playlist,
            [
                "shortBylineText",
                "runs",
                0,
                "navigationEndpoint",
                "browseEndpoint",
                "browseId",
            ],
        )
        component: Dict[str, Any] = {
            "type": "playlist",
            "id": pid,
            "title": self._get_value(playlist, ["title", "simpleText"]),
            "videoCount": self._get_value(
                playlist, ["videoCountShortText", "simpleText"]
            ),
            "thumbnails": self._get_value(playlist, ["thumbnail", "thumbnails"]),
            "channel": {
                "name": self._get_value(
                    playlist, ["shortBylineText", "runs", 0, "text"]
                ),
                "id": cid,
                "link": build_channel_url(cid),
            },
            "link": build_playlist_url(pid),
        }
        return component
