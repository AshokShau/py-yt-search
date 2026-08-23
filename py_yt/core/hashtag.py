import json
import logging
from typing import Any, Dict, List, Optional, Union

from py_yt.core.constants import (
    ResultMode,
    contentPath,
    continuationKeyPath,
    hashtagBrowseKey,
    hashtagContinuationVideosPath,
    hashtagElementKey,
    hashtagVideosPath,
    richItemKey,
    videoElementKey,
)
from py_yt.core.requests import RequestCore
from py_yt.handlers.componenthandler import ComponentHandler

logger = logging.getLogger(__name__)


class HashtagCore(RequestCore, ComponentHandler):
    response: Optional[str] = None
    resultComponents: List[Dict[str, Any]] = []

    def __init__(
        self,
        hashtag: str,
        limit: int,
        language: str,
        region: str,
        timeout: float,
        proxy: Optional[str] = None,
    ) -> None:
        super().__init__(timeout=timeout, proxy=proxy)
        self.hashtag: str = hashtag
        self.limit: int = limit
        self.language: str = language
        self.region: str = region
        self.timeout: float = timeout
        self.continuationKey: Optional[str] = None
        self.params: Optional[str] = None

    def result(self, mode: int = ResultMode.dict) -> Union[str, Dict[str, Any]]:
        """Returns the hashtag videos."""
        if mode == ResultMode.json:
            return json.dumps({"result": self.resultComponents}, indent=4)
        return {"result": self.resultComponents}

    async def next(self) -> bool:
        """Gets the videos from the next page."""
        self.response = None
        self.resultComponents = []
        if not self.params:
            await self._get_params()
        if self.continuationKey or self.params:
            await self._make_request()
            self._get_components()
        return bool(self.resultComponents)

    async def _get_params(self) -> None:
        self.url = self._build_url("search")
        self.data = self._build_payload(
            language=self.language,
            region=self.region,
            query="#" + self.hashtag,
        )

        resp = await self.post_request()
        if resp is None:
            raise Exception("ERROR: Could not make request.")

        try:
            response_json = await resp.json()
        except Exception as e:
            logger.error(
                "Failed to parse JSON response in hashtag _get_params", exc_info=True
            )
            raise Exception("ERROR: Could not make request.") from e

        content = self._get_value(response_json, contentPath)
        items = self._get_value(content, [0, "itemSectionRenderer", "contents"])
        if items and isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and hashtagElementKey in item:
                    self.params = self._get_value(
                        item[hashtagElementKey],
                        ["onTapCommand", "browseEndpoint", "params"],
                    )
                    return

    async def _make_request(self) -> None:
        if self.params is None:
            return
        self.url = self._build_url("browse")
        self.data = self._build_payload(
            language=self.language,
            region=self.region,
            browseId=hashtagBrowseKey,
            params=self.params,
            continuation=self.continuationKey,
        )

        resp = await self.post_request()
        if resp is None:
            raise Exception("ERROR: Could not make request.")

        try:
            raw_data = await resp.read()
            self.response = raw_data.decode("utf-8", errors="ignore")
        except Exception as e:
            logger.error(
                "Failed to read response in hashtag _make_request", exc_info=True
            )
            raise Exception("ERROR: Could not make request.") from e

    def _get_components(self) -> None:
        if self.response is None:
            return
        self.resultComponents = []
        try:
            data = json.loads(self.response)
            if not self.continuationKey:
                responseSource = self._get_value(data, hashtagVideosPath)
            else:
                responseSource = self._get_value(
                    data,
                    hashtagContinuationVideosPath,
                )

            if responseSource and isinstance(responseSource, list):
                for element in responseSource:
                    if not isinstance(element, dict):
                        continue
                    if richItemKey in element:
                        richItemElement = self._get_value(
                            element, [richItemKey, "content"]
                        )
                        if (
                            isinstance(richItemElement, dict)
                            and videoElementKey in richItemElement
                        ):
                            videoComponent = self._get_video_component(richItemElement)
                            self.resultComponents.append(videoComponent)
                    if len(self.resultComponents) >= self.limit:
                        break
                if responseSource:
                    self.continuationKey = self._get_value(
                        responseSource[-1],
                        continuationKeyPath,
                    )
        except Exception as e:
            logger.error("Could not parse YouTube hashtag response", exc_info=True)
            raise Exception("ERROR: Could not parse YouTube response.") from e
