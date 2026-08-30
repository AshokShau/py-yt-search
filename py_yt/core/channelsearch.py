import json
import logging
from typing import Any, Callable, Dict, List, Optional, Union

from py_yt.core.constants import ResultMode
from py_yt.core.requests import RequestCore
from py_yt.handlers.componenthandler import ComponentHandler

logger = logging.getLogger(__name__)


class ChannelSearchCore(RequestCore, ComponentHandler):
    response: Optional[Union[List[Any], Dict[str, Any]]] = None
    responseSource: Optional[Any] = None
    resultComponents: List[Dict[str, Any]] = []

    def __init__(
        self,
        query: str,
        language: str,
        region: str,
        search_preferences: str,
        browse_id: Optional[str] = None,
        timeout: float = 7.0,
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
        self.language: str = language
        self.region: str = region
        self.browseId: Optional[str] = self._extract_channel_id(browse_id) if browse_id else None
        self.searchPreferences: str = search_preferences
        self.continuationKey: Optional[str] = None
        self.timeout: float = timeout

    def _extract_channel_id(self, browse_id_or_url: str) -> str:
        clean = browse_id_or_url.strip()
        if "youtube.com/channel/" in clean:
            return clean.split("youtube.com/channel/")[1].split("/")[0].split("?")[0]
        return clean

    async def next(self) -> Dict[str, Any]:
        if not self.browseId:
            await self._resolve_browse_id()
        if not self.browseId:
            return {"result": []}

        await self._make_request()
        self._parse_channel_search_source()
        raw_elements: List[Any] = (
            self.response if isinstance(self.response, list) else []
        )
        components = self._get_channel_search_component(raw_elements)
        self.response = components
        return {"result": components}

    def _parse_channel_search_source(self) -> None:
        try:
            if not isinstance(self.response, dict):
                self.response = []
                return

            contents = (
                self.response.get("contents", {})
                .get("twoColumnBrowseResultsRenderer", {})
                .get("tabs", [])
            )
            if not contents:
                self.response = []
                return

            last_tab = contents[-1]
            if "expandableTabRenderer" in last_tab:
                renderer = last_tab["expandableTabRenderer"]
                if "content" in renderer:
                    self.response = renderer["content"]["sectionListRenderer"][
                        "contents"
                    ]
                else:
                    self.response = []
            elif "tabRenderer" in last_tab:
                tab_renderer = last_tab["tabRenderer"]
                if "content" in tab_renderer:
                    self.response = tab_renderer["content"]["sectionListRenderer"][
                        "contents"
                    ]
                else:
                    self.response = []
            else:
                self.response = []
        except Exception as e:
            logger.error(
                "Could not parse channel search YouTube response", exc_info=True
            )
            raise Exception("ERROR: Could not parse YouTube response.") from e

    async def _resolve_browse_id(self) -> None:
        from py_yt.core.search import SearchCore
        from py_yt.core.constants import SearchMode
        search = SearchCore(
            self.query,
            1,
            self.language,
            self.region,
            SearchMode.channels,
            self.timeout,
            proxy=getattr(self, "proxy", None),
        )
        res = await search.next()
        results = res.get("result", [])
        if results and isinstance(results, list):
            first_channel = results[0]
            if isinstance(first_channel, dict) and first_channel.get("id"):
                self.browseId = first_channel["id"]

    def _get_request_body(self) -> None:
        self.url = self._build_url("browse")
        self.data = self._build_payload(
            language=self.language,
            region=self.region,
            query=self.query,
            params=self.searchPreferences,
            browseId=self.browseId,
        )

    async def _make_request(self) -> None:
        self._get_request_body()

        request = await self.post_request()
        if request is None:
            raise Exception("ERROR: Could not make request.")

        try:
            self.response = await request.json()
        except Exception as e:
            logger.error(
                "Failed to parse JSON response from channel search", exc_info=True
            )
            raise Exception("ERROR: Could not make request.") from e

    def result(self, mode: int = ResultMode.dict) -> Union[str, Dict[str, Any]]:
        """Returns the search result."""
        if mode == ResultMode.json:
            return json.dumps({"result": self.response}, indent=4)
        return {"result": self.response or {}}
