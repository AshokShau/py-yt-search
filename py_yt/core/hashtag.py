import copy
import json
from typing import Union
from urllib.parse import urlencode
import aiohttp

from py_yt.core.session import get_session
from py_yt.core.constants import (
    videoElementKey,
    ResultMode,
    requestPayload,
    searchKey,
    userAgent,
    contentPath,
    hashtagElementKey,
    hashtagBrowseKey,
    hashtagVideosPath,
    hashtagContinuationVideosPath,
    richItemKey,
    continuationKeyPath,
)
from py_yt.handlers.componenthandler import ComponentHandler


class HashtagCore(ComponentHandler):
    response = None
    resultComponents = []

    def __init__(
        self,
        hashtag: str,
        limit: int,
        language: str,
        region: str,
        timeout: int,
        proxy: str | None = None,
    ):
        self.hashtag = hashtag
        self.limit = limit
        self.language = language
        self.region = region
        self.timeout = timeout
        self.proxy = proxy
        self.continuationKey = None
        self.params = None

    def result(self, mode: int = ResultMode.dict) -> Union[str, dict]:
        """Returns the hashtag videos.
        Args:
            mode (int, optional): Sets the type of result. Defaults to ResultMode.dict.
        Returns:
            Union[str, dict]: Returns JSON or dictionary.
        """
        if mode == ResultMode.json:
            return json.dumps({"result": self.resultComponents}, indent=4)
        elif mode == ResultMode.dict:
            return {"result": self.resultComponents}

    async def next(self) -> bool:
        """Gets the videos from the next page. Call result
        Returns:
            bool: Returns True if getting more results was successful.
        """
        self.response = None
        self.resultComponents = []
        if self.continuationKey:
            await self._makeRequest()
            self._getComponents()
        if self.resultComponents:
            return True
        return False

    async def _getParams(self) -> None:
        requestBody = copy.deepcopy(requestPayload)
        requestBody["query"] = "#" + self.hashtag
        requestBody["client"] = {
            "hl": self.language,
            "gl": self.region,
        }
        try:
            session = await get_session()
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            response = await session.post(
                "https://www.youtube.com/youtubei/v1/search",
                params={
                    "key": searchKey,
                },
                headers={
                    "User-Agent": userAgent,
                },
                json=requestBody,
                proxy=self.proxy,
                timeout=timeout,
            )
            response_json = await response.json()
        except:
            raise Exception("ERROR: Could not make request.")
        content = self._getValue(response_json, contentPath)
        for item in self._getValue(content, [0, "itemSectionRenderer", "contents"]):
            if hashtagElementKey in item.keys():
                self.params = self._getValue(
                    item[hashtagElementKey],
                    ["onTapCommand", "browseEndpoint", "params"],
                )
                return

    async def _makeRequest(self) -> None:
        if self.params == None:
            return
        requestBody = copy.deepcopy(requestPayload)
        requestBody["browseId"] = hashtagBrowseKey
        requestBody["params"] = self.params
        requestBody["client"] = {
            "hl": self.language,
            "gl": self.region,
        }
        if self.continuationKey:
            requestBody["continuation"] = self.continuationKey
        try:
            session = await get_session()
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            response = await session.post(
                "https://www.youtube.com/youtubei/v1/browse",
                params={
                    "key": searchKey,
                },
                headers={
                    "User-Agent": userAgent,
                },
                json=requestBody,
                proxy=self.proxy,
                timeout=timeout,
            )
            self.response = await response.read()
        except:
            raise Exception("ERROR: Could not make request.")

    def _getComponents(self) -> None:
        if self.response == None:
            return
        self.resultComponents = []
        try:
            if not self.continuationKey:
                responseSource = self._getValue(
                    json.loads(self.response), hashtagVideosPath
                )
            else:
                responseSource = self._getValue(
                    json.loads(self.response), hashtagContinuationVideosPath
                )
            if responseSource:
                for element in responseSource:
                    if richItemKey in element.keys():
                        richItemElement = self._getValue(
                            element, [richItemKey, "content"]
                        )
                        if videoElementKey in richItemElement.keys():
                            videoComponent = self._getVideoComponent(richItemElement)
                            self.resultComponents.append(videoComponent)
                    if len(self.resultComponents) >= self.limit:
                        break
                self.continuationKey = self._getValue(
                    responseSource[-1], continuationKeyPath
                )
        except:
            raise Exception("ERROR: Could not parse YouTube response.")
