import copy
from typing import Union
from urllib.parse import urlencode

from py_yt.core.componenthandler import getVideoId
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
        self.resultComponents = []

    def _getRequestBody(self):
        requestBody = copy.deepcopy(requestPayload)
        requestBody["context"]["client"]["clientName"] = "MWEB"
        requestBody["context"]["client"]["clientVersion"] = "2.20240425.01.00"
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

    async def _makeAsyncRequest(self) -> None:
        self._getRequestBody()
        response = await self.asyncPostRequest()
        if response:
            self.responseSource = response.json()
        else:
            raise Exception("ERROR: Could not make request.")

    def _getValue(self, source: dict, path: list) -> Union[str, int, dict, list, None]:
        value = source
        for key in path:
            if type(key) is str:
                if isinstance(value, dict) and key in value.keys():
                    value = value[key]
                else:
                    value = None
                    break
            elif type(key) is int:
                if isinstance(value, list) and len(value) > key:
                    value = value[key]
                else:
                    value = None
                    break
        return value

    async def next(self) -> dict:
        self.resultComponents = []
        await self._makeAsyncRequest()
        self._parseSource()
        return {
            "result": self.resultComponents,
        }

    def _parseSource(self) -> None:
        if not self.responseSource:
            return
        
        contents = []
        if not self.continuationKey:
            secondary_results = self._getValue(self.responseSource, ["contents", "twoColumnWatchNextResults", "secondaryResults", "secondaryResults", "results"])
            if not secondary_results:
                 secondary_results = self._getValue(self.responseSource, ["contents", "singleColumnWatchNextResults", "pivot", "pivotRenderer", "contents"])
            
            if not secondary_results:
                secondary_results = self._getValue(self.responseSource, ["contents", "singleColumnWatchNextResults", "results", "results", "contents"])

            if secondary_results:
                contents = secondary_results
        else:
            continuation_actions = self._getValue(self.responseSource, ["onResponseReceivedEndpoints"])
            if continuation_actions:
                for action in continuation_actions:
                    if "appendContinuationItemsAction" in action:
                        contents.extend(action["appendContinuationItemsAction"]["continuationItems"])

        if not contents:
            return

        for element in contents:
            if "compactVideoRenderer" in element:
                self.resultComponents.append(self._getCompactVideoComponent(element))
            elif "videoWithContextRenderer" in element:
                self.resultComponents.append(self._getVideoWithContextComponent(element))
            elif "compactPlaylistRenderer" in element:
                self.resultComponents.append(self._getCompactPlaylistComponent(element))
            elif "itemSectionRenderer" in element:
                nested_contents = self._getValue(element, ["itemSectionRenderer", "contents"])
                if nested_contents:
                    for nested in nested_contents:
                        if len(self.resultComponents) >= self.limit:
                             break
                        if "compactVideoRenderer" in nested:
                            self.resultComponents.append(self._getCompactVideoComponent(nested))
                        elif "videoWithContextRenderer" in nested:
                            self.resultComponents.append(self._getVideoWithContextComponent(nested))
            elif "continuationItemRenderer" in element:
                self.continuationKey = self._getValue(element, ["continuationItemRenderer", "continuationEndpoint", "continuationCommand", "token"])

            if len(self.resultComponents) >= self.limit:
                break

    def _getCompactVideoComponent(self, element: dict) -> dict:
        video = element["compactVideoRenderer"]
        component = {
            "type": "video",
            "id": self._getValue(video, ["videoId"]),
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
                "id": self._getValue(video, ["shortBylineText", "runs", 0, "navigationEndpoint", "browseEndpoint", "browseId"]),
            },
            "accessibility": {
                "title": self._getValue(video, ["title", "accessibility", "accessibilityData", "label"]),
                "duration": self._getValue(video, ["lengthText", "accessibility", "accessibilityData", "label"]),
            },
        }
        component["link"] = "https://www.youtube.com/watch?v=" + component["id"]
        if component["channel"]["id"]:
            component["channel"]["link"] = "https://www.youtube.com/channel/" + component["channel"]["id"]
        return component

    def _getVideoWithContextComponent(self, element: dict) -> dict:
        video = element["videoWithContextRenderer"]
        component = {
            "type": "video",
            "id": self._getValue(video, ["videoId"]),
            "title": self._getValue(video, ["headline", "runs", 0, "text"]),
            "publishedTime": self._getValue(video, ["publishedTimeText", "runs", 0, "text"]),
            "duration": self._getValue(video, ["lengthText", "runs", 0, "text"]),
            "viewCount": {
                "text": self._getValue(video, ["shortViewCountText", "runs", 0, "text"]),
                "short": self._getValue(video, ["shortViewCountText", "runs", 0, "text"]),
            },
            "thumbnails": self._getValue(video, ["thumbnail", "thumbnails"]),
            "channel": {
                "name": self._getValue(video, ["shortBylineText", "runs", 0, "text"]),
                "id": self._getValue(video, ["shortBylineText", "runs", 0, "navigationEndpoint", "browseEndpoint", "browseId"]),
            },
            "accessibility": {
                "title": self._getValue(video, ["headline", "accessibility", "accessibilityData", "label"]),
                "duration": self._getValue(video, ["lengthText", "accessibility", "accessibilityData", "label"]),
            },
        }
        component["link"] = "https://www.youtube.com/watch?v=" + component["id"]
        if component["channel"]["id"]:
            component["channel"]["link"] = "https://www.youtube.com/channel/" + component["channel"]["id"]
        return component

    def _getCompactPlaylistComponent(self, element: dict) -> dict:
        playlist = element["compactPlaylistRenderer"]
        component = {
            "type": "playlist",
            "id": self._getValue(playlist, ["playlistId"]),
            "title": self._getValue(playlist, ["title", "simpleText"]),
            "videoCount": self._getValue(playlist, ["videoCountShortText", "simpleText"]),
            "thumbnails": self._getValue(playlist, ["thumbnail", "thumbnails"]),
            "channel": {
                "name": self._getValue(playlist, ["shortBylineText", "runs", 0, "text"]),
                "id": self._getValue(playlist, ["shortBylineText", "runs", 0, "navigationEndpoint", "browseEndpoint", "browseId"]),
            },
        }
        component["link"] = "https://www.youtube.com/playlist?list=" + component["id"]
        if component["channel"]["id"]:
            component["channel"]["link"] = "https://www.youtube.com/channel/" + component["channel"]["id"]
        return component
