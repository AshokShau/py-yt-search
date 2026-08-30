import json
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

from py_yt.core.constants import ResultMode
from py_yt.core.requests import RequestCore

logger = logging.getLogger(__name__)


class SuggestionsCore(RequestCore):
    """Gets search suggestions for the given query."""

    response: Optional[str] = None
    responseSource: Optional[Any] = None

    def __init__(
        self,
        language: str = "en",
        region: str = "US",
        timeout: Optional[float] = None,
        proxy: Optional[str] = None,
    ) -> None:
        super().__init__(timeout=timeout if timeout is not None else 7.0, proxy=proxy)
        self.language: str = language
        self.region: str = region
        self.timeout: float = timeout if timeout is not None else 7.0

    def _post_request_processing(self, mode: int) -> Union[Dict[str, List[str]], str]:
        search_suggestions: List[str] = []

        self._parse_source()
        if isinstance(self.responseSource, list):
            for element in self.responseSource:
                if isinstance(element, list):
                    for searchSuggestionElement in element:
                        if (
                            isinstance(searchSuggestionElement, list)
                            and searchSuggestionElement
                        ):
                            search_suggestions.append(searchSuggestionElement[0])
                    break
        if mode == ResultMode.dict:
            return {"result": search_suggestions}
        elif mode == ResultMode.json:
            return json.dumps({"result": search_suggestions}, indent=4)
        return {"result": search_suggestions}

    async def _get(
        self, query: str, mode: int = ResultMode.dict
    ) -> Union[Dict[str, List[str]], str]:
        self.url = (
            "https://clients1.google.com/complete/search"
            + "?"
            + urlencode(
                {
                    "hl": self.language,
                    "gl": self.region,
                    "q": query,
                    "client": "youtube",
                    "gs_ri": "youtube",
                    "ds": "yt",
                }
            )
        )

        await self._make_request()
        return self._post_request_processing(mode)

    def _parse_source(self) -> None:
        try:
            resp = self.response or ""
            start_index = resp.index("([") + 1
            end_index = resp.rindex("])") + 1
            self.responseSource = json.loads(resp[start_index:end_index])
        except (ValueError, json.JSONDecodeError) as e:
            logger.error(
                "Could not parse YouTube response. Raw response: %r",
                getattr(self, "response", None),
                exc_info=True,
            )
            raise Exception("ERROR: Could not parse YouTube response.") from e

    async def _make_request(self) -> None:
        request = await self.get_request()
        if request is None:
            raise Exception("ERROR: Could not make request.")
        self.response = await request.text()

    def _result(self, mode: int) -> Union[Dict[str, List[str]], str]:
        return self._post_request_processing(mode)
