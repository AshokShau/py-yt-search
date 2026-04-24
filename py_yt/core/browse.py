import copy
import json
from typing import Union
from urllib.parse import urlencode

from py_yt.core.constants import (
    requestPayload,
    searchKey,
    ResultMode,
)
from py_yt.core.requests import RequestCore
from py_yt.handlers.componenthandler import ComponentHandler
from py_yt.core.componenthandler import getValue


class BrowseCore(RequestCore, ComponentHandler):
    def __init__(
        self,
        browse_id: str,
        limit: int = 20,
        language: str = "en",
        region: str = "US",
        timeout: int = 20,
        max_retries: int = 0,
        proxy: str | None = None,
    ):
        super().__init__(timeout=timeout, max_retries=max_retries, proxy=proxy)
        self.browseId = browse_id
        self.limit = limit
        self.language = language
        self.region = region
        self.continuationKey = None
        self.resultComponents = []

    def _getRequestBody(self):
        requestBody = copy.deepcopy(requestPayload)

        requestBody["context"]["client"]["clientName"] = "MWEB"
        requestBody["context"]["client"]["clientVersion"] = "2.20240425.01.00"
        requestBody["browseId"] = self.browseId
        requestBody["context"]["client"]["hl"] = self.language
        requestBody["context"]["client"]["gl"] = self.region
        if self.continuationKey:
            requestBody["continuation"] = self.continuationKey
        
        self.url = (
            "https://www.youtube.com/youtubei/v1/browse"
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
            self.response = await response.text()
            self.responseSource = await response.json()
        else:
            raise Exception("ERROR: Could not make request.")

    def _getValue(self, source: dict, path: list) -> Union[str, int, dict, list, None]:
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
        if "contents" in self.responseSource:
            tab_contents = self._getValue(self.responseSource, ["contents", "twoColumnBrowseResultsRenderer", "tabs", 0, "tabRenderer", "content"])
            if not tab_contents:
                tab_contents = self._getValue(self.responseSource, ["contents", "singleColumnBrowseResultsRenderer", "tabs", 0, "tabRenderer", "content"])
            
            if not tab_contents:
                tab_contents = self.responseSource.get("contents")

            if isinstance(tab_contents, list):
                contents = tab_contents
            elif tab_contents:
                if "richGridRenderer" in tab_contents:
                    contents = self._getValue(tab_contents, ["richGridRenderer", "contents"])
                elif "sectionListRenderer" in tab_contents:
                    contents = self._getValue(tab_contents, ["sectionListRenderer", "contents"])
        elif "onResponseReceivedActions" in self.responseSource:
            contents = self._getValue(self.responseSource, ["onResponseReceivedActions", 0, "appendContinuationItemsAction", "continuationItems"])

        if not contents:
            return

        for element in contents:
            if "richItemRenderer" in element:
                content = element["richItemRenderer"]["content"]
                if "videoRenderer" in content:
                    self.resultComponents.append(self._getVideoComponent(content))
                elif "playlistRenderer" in content:
                    self.resultComponents.append(self._getPlaylistComponent(content))
            elif "videoRenderer" in element:
                self.resultComponents.append(self._getVideoComponent(element))
            elif "playlistRenderer" in element:
                self.resultComponents.append(self._getPlaylistComponent(element))
            elif "richSectionRenderer" in element:
                nested_contents = self._getValue(element, ["richSectionRenderer", "content", "richShelfRenderer", "contents"])
                if nested_contents:
                    for nested in nested_contents:
                         if "richItemRenderer" in nested:
                             nested_content = nested["richItemRenderer"]["content"]
                             if "videoRenderer" in nested_content:
                                 self.resultComponents.append(self._getVideoComponent(nested_content))
            elif "continuationItemRenderer" in element:
                self.continuationKey = self._getValue(element, ["continuationItemRenderer", "continuationEndpoint", "continuationCommand", "token"])

            if len(self.resultComponents) >= self.limit:
                break
