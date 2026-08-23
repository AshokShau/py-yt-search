import copy
from typing import Any, Dict, List, Union
from urllib.parse import urlencode

from py_yt.core.componenthandler import getVideoId, getValue
from py_yt.core.constants import (
    requestPayload,
    searchKey,
)
from py_yt.core.requests import RequestCore
from py_yt.handlers.componenthandler import ComponentHandler


class RelatedVideosCore(RequestCore, ComponentHandler):
    def __init__(
        self,
        video_link: str,
        limit: int = 20,
        language: str = "en",
        region: str = "US",
        timeout: int = 20,
        max_retries: int = 0,
        proxy: str | None = None,
    ):
        super().__init__(timeout=timeout, max_retries=max_retries, proxy=proxy)
        self.video_link = video_link
        self.limit = limit
        self.language = language
        self.region = region
        self.continuationKey = None
        self.resultComponents: List[Dict[str, Any]] = []

    def _getRequestBody(self):
        requestBody = copy.deepcopy(requestPayload)
        requestBody["context"]["client"]["clientName"] = "MWEB"
        requestBody["context"]["client"]["clientVersion"] = "2.20260821.00.00"
        requestBody["videoId"] = getVideoId(self.video_link)
        requestBody["context"]["client"]["hl"] = self.language
        requestBody["context"]["client"]["gl"] = self.region
        if self.continuationKey:
            requestBody["continuation"] = self.continuationKey

        self.url = (
            "https://www.youtube.com/youtubei/v1/next"
            + "?"
            + urlencode(
                {
                    "key": searchKey,
                }
            )
        )
        self.data = requestBody

    async def _makeRequest(self) -> None:
        self._getRequestBody()
        response = await self.postRequest()
        if response:
            self.responseSource = await response.json()
        else:
            raise Exception("ERROR: Could not make request.")

    def _getValue(self, source: Any, path: List[Union[str, int, None]]) -> Any:
        return getValue(source, path)

    async def next(self) -> dict:
        self.resultComponents = []
        await self._makeRequest()
        self._parseSource()
        return {
            "result": self.resultComponents,
        }

    def _parseSource(self) -> None:
        if not self.responseSource:
            return

        contents = []
        if not self.continuationKey:
            secondary_results = self._getValue(
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
                secondary_results = self._getValue(
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
                secondary_results = self._getValue(
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
            continuation_actions = self._getValue(
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
                self.resultComponents.append(self._getCompactVideoComponent(element))
            elif "videoWithContextRenderer" in element:
                self.resultComponents.append(
                    self._getVideoWithContextComponent(element)
                )
            elif "compactPlaylistRenderer" in element:
                self.resultComponents.append(self._getCompactPlaylistComponent(element))
            elif "itemSectionRenderer" in element:
                nested_contents = self._getValue(
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
                                self._getCompactVideoComponent(nested)
                            )
                        elif "videoWithContextRenderer" in nested:
                            self.resultComponents.append(
                                self._getVideoWithContextComponent(nested)
                            )
            elif "continuationItemRenderer" in element:
                self.continuationKey = self._getValue(
                    element,
                    [
                        "continuationItemRenderer",
                        "continuationEndpoint",
                        "continuationCommand",
                        "token",
                    ],
                )

            if len(self.resultComponents) >= self.limit:
                break

    def _getCompactVideoComponent(self, element: dict) -> dict:
        video = element["compactVideoRenderer"]
        vid = self._getValue(video, ["videoId"])
        component = {
            "type": "video",
            "id": vid,
            "title": self._getValue(video, ["title", "simpleText"]),
            "publishedTime": self._getValue(video, ["publishedTimeText", "simpleText"]),
            "duration": self._getValue(video, ["lengthText", "simpleText"]),
            "viewCount": {
                "text": self._getValue(video, ["viewCountText", "simpleText"]),
                "short": self._getValue(video, ["shortViewCountText", "simpleText"]),
            },
            "thumbnails": self._getValue(video, ["thumbnail", "thumbnails"]),
            "channel": {
                "name": self._getValue(video, ["shortBylineText", "runs", 0, "text"]),
                "id": self._getValue(
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
        return component

    def _getVideoWithContextComponent(self, element: dict) -> dict:
        video = element["videoWithContextRenderer"]
        vid = self._getValue(video, ["videoId"])
        component = {
            "type": "video",
            "id": vid,
            "title": self._getValue(video, ["headline", "runs", 0, "text"]),
            "publishedTime": self._getValue(
                video, ["publishedTimeText", "runs", 0, "text"]
            ),
            "duration": self._getValue(video, ["lengthText", "runs", 0, "text"]),
            "viewCount": {
                "text": self._getValue(
                    video, ["shortViewCountText", "runs", 0, "text"]
                ),
                "short": self._getValue(
                    video, ["shortViewCountText", "runs", 0, "text"]
                ),
            },
            "thumbnails": self._getValue(video, ["thumbnail", "thumbnails"]),
            "channel": {
                "name": self._getValue(video, ["shortBylineText", "runs", 0, "text"]),
                "id": self._getValue(
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
            },
            "accessibility": {
                "title": self._getValue(
                    video, ["headline", "accessibility", "accessibilityData", "label"]
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
        return component

    def _getCompactPlaylistComponent(self, element: dict) -> dict:
        playlist = element["compactPlaylistRenderer"]
        pid = self._getValue(playlist, ["playlistId"])
        component = {
            "type": "playlist",
            "id": pid,
            "title": self._getValue(playlist, ["title", "simpleText"]),
            "videoCount": self._getValue(
                playlist, ["videoCountShortText", "simpleText"]
            ),
            "thumbnails": self._getValue(playlist, ["thumbnail", "thumbnails"]),
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
        }
        component["link"] = (
            "https://www.youtube.com/playlist?list=" + pid if pid else None
        )
        cid = component["channel"]["id"]
        if cid:
            component["channel"]["link"] = "https://www.youtube.com/channel/" + cid
        else:
            component["channel"]["link"] = None
        return component
