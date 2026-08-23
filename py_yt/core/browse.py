from typing import Any, Dict, List, Optional

from py_yt.core.requests import RequestCore
from py_yt.handlers.componenthandler import ComponentHandler


class BrowseCore(RequestCore, ComponentHandler):
    response: Optional[str] = None
    responseSource: Optional[Dict[str, Any]] = None

    def __init__(
        self,
        browse_id: str,
        limit: int = 20,
        language: str = "en",
        region: str = "US",
        timeout: float = 20.0,
        max_retries: int = 0,
        proxy: Optional[str] = None,
    ) -> None:
        super().__init__(timeout=timeout, max_retries=max_retries, proxy=proxy)
        self.browseId: str = browse_id
        self.limit: int = limit
        self.language: str = language
        self.region: str = region
        self.continuationKey: Optional[str] = None
        self.resultComponents: List[Dict[str, Any]] = []

    def _get_request_body(self) -> None:
        self.url = self._build_url("browse")
        self.data = self._build_payload(
            language=self.language,
            region=self.region,
            client_name="MWEB",
            client_version="2.20260821.00.00",
            browseId=self.browseId,
            continuation=self.continuationKey,
        )

    async def _make_request(self) -> None:
        self._get_request_body()
        response = await self.post_request()
        if response:
            self.response = await response.text()
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
        if not self.responseSource or not isinstance(self.responseSource, dict):
            return

        contents: List[Any] = []
        if "contents" in self.responseSource:
            tab_contents = self._get_value(
                self.responseSource,
                [
                    "contents",
                    "twoColumnBrowseResultsRenderer",
                    "tabs",
                    0,
                    "tabRenderer",
                    "content",
                ],
            )
            if not tab_contents:
                tab_contents = self._get_value(
                    self.responseSource,
                    [
                        "contents",
                        "singleColumnBrowseResultsRenderer",
                        "tabs",
                        0,
                        "tabRenderer",
                        "content",
                    ],
                )

            if not tab_contents:
                tab_contents = self.responseSource.get("contents")

            if isinstance(tab_contents, list):
                contents = tab_contents
            elif isinstance(tab_contents, dict):
                if "richGridRenderer" in tab_contents:
                    contents = self._get_value(
                        tab_contents, ["richGridRenderer", "contents"]
                    ) or []
                elif "sectionListRenderer" in tab_contents:
                    contents = self._get_value(
                        tab_contents, ["sectionListRenderer", "contents"]
                    ) or []
        elif "onResponseReceivedActions" in self.responseSource:
            contents = self._get_value(
                self.responseSource,
                [
                    "onResponseReceivedActions",
                    0,
                    "appendContinuationItemsAction",
                    "continuationItems",
                ],
            ) or []

        if not contents or not isinstance(contents, list):
            return

        for element in contents:
            if not isinstance(element, dict):
                continue
            if "richItemRenderer" in element:
                content = element["richItemRenderer"].get("content", {})
                if isinstance(content, dict):
                    if "videoRenderer" in content:
                        self.resultComponents.append(self._get_video_component(content))
                    elif "playlistRenderer" in content:
                        self.resultComponents.append(
                            self._get_playlist_component(content)
                        )
            elif "videoRenderer" in element:
                self.resultComponents.append(self._get_video_component(element))
            elif "playlistRenderer" in element:
                self.resultComponents.append(self._get_playlist_component(element))
            elif "richSectionRenderer" in element:
                nested_contents = self._get_value(
                    element,
                    [
                        "richSectionRenderer",
                        "content",
                        "richShelfRenderer",
                        "contents",
                    ],
                )
                if nested_contents and isinstance(nested_contents, list):
                    for nested in nested_contents:
                        if isinstance(nested, dict) and "richItemRenderer" in nested:
                            nested_content = nested["richItemRenderer"].get(
                                "content", {}
                            )
                            if (
                                isinstance(nested_content, dict)
                                and "videoRenderer" in nested_content
                            ):
                                self.resultComponents.append(
                                    self._get_video_component(nested_content)
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
