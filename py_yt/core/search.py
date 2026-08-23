import json
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from py_yt.core.constants import (
    ResultMode,
    channelElementKey,
    playlistElementKey,
    richItemKey,
    shelfElementKey,
    videoElementKey,
)
from py_yt.core.requests import RequestCore
from py_yt.handlers.componenthandler import ComponentHandler
from py_yt.handlers.requesthandler import RequestHandler


class SearchCore(RequestCore, RequestHandler, ComponentHandler):
    response: Optional[Union[str, List[Any], Dict[str, Any]]] = None
    responseSource: Optional[Any] = None
    resultComponents: List[Dict[str, Any]] = []
    searchMode: Tuple[bool, bool, bool] = (True, True, True)

    def __init__(
        self,
        query: str,
        limit: int,
        language: str,
        region: str,
        searchPreferences: str,
        timeout: float,
        with_live: bool = True,
        max_retries: int = 2,
        proxy: Optional[str] = None,
        visitor_data: Optional[str] = None,
        po_token: Optional[str] = None,
        po_token_verifier: Optional[Callable[..., Any]] = None,
    ) -> None:
        super().__init__(
            timeout=timeout,
            max_retries=max_retries,
            proxy=proxy,
            visitor_data=visitor_data,
            po_token=po_token,
            po_token_verifier=po_token_verifier,
        )
        self.query: str = query
        self.limit: int = limit
        self.language: str = language
        self.region: str = region
        self.searchPreferences: str = searchPreferences
        self.timeout: float = timeout
        self.with_live: bool = with_live
        self.continuationKey: Optional[str] = None

    def _get_request_body(self) -> None:
        q = self.query
        is_video_id_or_url = False
        video_patterns = [
            r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})",
            r"(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})",
            r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})",
            r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([a-zA-Z0-9_-]{11})",
            r"^([a-zA-Z0-9_-]{11})$",
        ]
        for pattern in video_patterns:
            if match := re.search(pattern, self.query):
                is_video_id_or_url = True
                q = match.group(1)
                break

        params = self.searchPreferences if (self.searchPreferences and not is_video_id_or_url) else None

        self.url = self._build_url("search")
        self.data = self._build_payload(
            language=self.language,
            region=self.region,
            query=q,
            params=params,
            continuation=self.continuationKey,
        )

    async def _make_request(self) -> None:
        self._get_request_body()
        request = await self.post_request()
        if request:
            self.response = await request.text()
        else:
            raise Exception("ERROR: Could not make request.")

    def result(self, mode: int = ResultMode.dict) -> Union[str, Dict[str, Any]]:
        """Returns the search result in dict or JSON format."""
        if mode == ResultMode.json:
            return json.dumps({"result": self.resultComponents}, indent=4)
        return {"result": self.resultComponents}

    async def next(self) -> Dict[str, Any]:
        self.response = None
        self.responseSource = None
        self.resultComponents = []
        await self._make_request()
        self._parse_source()
        self._get_components(*self.searchMode)
        return {
            "result": self.resultComponents,
        }

    def _get_components(
        self, find_videos: bool, find_channels: bool, find_playlists: bool
    ) -> None:
        self.resultComponents = []
        if not self.responseSource or not isinstance(self.responseSource, list):
            return

        for element in self.responseSource:
            if not isinstance(element, dict):
                continue
            if videoElementKey in element and find_videos:
                videoComponent = self._get_video_component(element)
                if (
                    not self.with_live
                    and videoComponent["duration"] is None
                    and videoComponent["publishedTime"] is None
                ):
                    continue
                self.resultComponents.append(videoComponent)
            if channelElementKey in element and find_channels:
                self.resultComponents.append(self._get_channel_component(element))
            if (
                playlistElementKey in element or "lockupViewModel" in element
            ) and find_playlists:
                self.resultComponents.append(self._get_playlist_component(element))
            if shelfElementKey in element and find_videos:
                shelfComp = self._get_shelf_component(element)
                shelfElements = (
                    shelfComp.get("elements") if isinstance(shelfComp, dict) else None
                )
                if shelfElements and isinstance(shelfElements, list):
                    for shelfElement in shelfElements:
                        if isinstance(shelfElement, dict):
                            videoComponent = self._get_video_component(
                                shelfElement,
                                shelf_title=shelfComp.get("title"),
                            )
                            if (
                                not self.with_live
                                and videoComponent["duration"] is None
                                and videoComponent["publishedTime"] is None
                            ):
                                continue
                            self.resultComponents.append(videoComponent)
            if richItemKey in element and find_videos:
                richItemElement = self._get_value(element, [richItemKey, "content"])
                if (
                    isinstance(richItemElement, dict)
                    and videoElementKey in richItemElement
                ):
                    videoComponent = self._get_video_component(richItemElement)
                    if (
                        not self.with_live
                        and videoComponent["duration"] is None
                        and videoComponent["publishedTime"] is None
                    ):
                        continue
                    self.resultComponents.append(videoComponent)
            if len(self.resultComponents) >= self.limit:
                break
