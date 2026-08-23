import copy
import json
import logging
from typing import Any, Dict, List, Union
from urllib.parse import urlencode

from py_yt.core.constants import (
    videoElementKey,
    ResultMode,
    requestPayload,
    searchKey,
    contentPath,
    hashtagElementKey,
    hashtagBrowseKey,
    hashtagVideosPath,
    hashtagContinuationVideosPath,
    richItemKey,
    continuationKeyPath,
)
from py_yt.core.requests import RequestCore
from py_yt.handlers.componenthandler import ComponentHandler

logger = logging.getLogger(__name__)


class HashtagCore(RequestCore, ComponentHandler):
    response = None
    resultComponents: List[Dict[str, Any]] = []

    def __init__(
        self,
        hashtag: str,
        limit: int,
        language: str,
        region: str,
        timeout: int,
        proxy: str | None = None,
    ):
        super().__init__(timeout=timeout, proxy=proxy)
        self.hashtag = hashtag
        self.limit = limit
        self.language = language
        self.region = region
        self.timeout = timeout
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
        return {"result": self.resultComponents}

    async def next(self) -> bool:
        """Gets the videos from the next page.

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
        requestBody: Dict[str, Any] = copy.deepcopy(requestPayload)
        requestBody["query"] = "#" + self.hashtag
        client_dict = requestBody["context"]["client"]
        client_dict["hl"] = self.language
        client_dict["gl"] = self.region

        self.url = (
            "https://www.youtube.com/youtubei/v1/search"
            + "?"
            + urlencode({"key": searchKey})
        )
        self.data = requestBody

        resp = await self.postRequest()
        if resp is None:
            raise Exception("ERROR: Could not make request.")

        try:
            response_json = await resp.json()
        except Exception as e:
            logger.error(
                "Failed to parse JSON response in hashtag _getParams", exc_info=True
            )
            raise Exception("ERROR: Could not make request.") from e

        content = self._getValue(response_json, list(contentPath))  # type: ignore[arg-type]
        items = self._getValue(content, [0, "itemSectionRenderer", "contents"])
        if items and isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and hashtagElementKey in item:
                    self.params = self._getValue(
                        item[hashtagElementKey],
                        ["onTapCommand", "browseEndpoint", "params"],
                    )
                    return

    async def _makeRequest(self) -> None:
        if self.params is None:
            return
        requestBody: Dict[str, Any] = copy.deepcopy(requestPayload)
        requestBody["browseId"] = hashtagBrowseKey
        requestBody["params"] = self.params
        client_dict = requestBody["context"]["client"]
        client_dict["hl"] = self.language
        client_dict["gl"] = self.region
        if self.continuationKey:
            requestBody["continuation"] = self.continuationKey

        self.url = (
            "https://www.youtube.com/youtubei/v1/browse"
            + "?"
            + urlencode({"key": searchKey})
        )
        self.data = requestBody

        resp = await self.postRequest()
        if resp is None:
            raise Exception("ERROR: Could not make request.")

        try:
            raw_data = await resp.read()
            self.response = raw_data.decode("utf-8", errors="ignore")
        except Exception as e:
            logger.error(
                "Failed to read response in hashtag _makeRequest", exc_info=True
            )
            raise Exception("ERROR: Could not make request.") from e

    def _getComponents(self) -> None:
        if self.response is None:
            return
        self.resultComponents = []
        try:
            data = json.loads(self.response)
            if not self.continuationKey:
                responseSource = self._getValue(data, list(hashtagVideosPath))  # type: ignore[arg-type]
            else:
                responseSource = self._getValue(
                    data,
                    list(hashtagContinuationVideosPath),  # type: ignore[arg-type]
                )

            if responseSource and isinstance(responseSource, list):
                for element in responseSource:
                    if not isinstance(element, dict):
                        continue
                    if richItemKey in element:
                        richItemElement = self._getValue(
                            element, [richItemKey, "content"]
                        )
                        if (
                            isinstance(richItemElement, dict)
                            and videoElementKey in richItemElement
                        ):
                            videoComponent = self._getVideoComponent(richItemElement)
                            self.resultComponents.append(videoComponent)
                    if len(self.resultComponents) >= self.limit:
                        break
                if responseSource:
                    self.continuationKey = self._getValue(
                        responseSource[-1],
                        list(continuationKeyPath),  # type: ignore[arg-type]
                    )
        except Exception as e:
            logger.error("Could not parse YouTube hashtag response", exc_info=True)
            raise Exception("ERROR: Could not parse YouTube response.") from e
