import json
import logging
from typing import Any, Optional

from py_yt.core.constants import (
    contentPath,
    itemSectionKey,
    continuationItemKey,
    continuationKeyPath,
    fallbackContentPath,
    continuationContentPath,
)
from py_yt.handlers.componenthandler import ComponentHandler

logger = logging.getLogger(__name__)


class RequestHandler(ComponentHandler):
    response: Optional[str] = None
    continuationKey: Optional[str] = None
    responseSource: Optional[Any] = None

    def _parseSource(self) -> None:
        try:
            resp = self.response or ""
            parsed_data = json.loads(resp) if resp else {}
            c_path = list(contentPath)  # type: ignore[arg-type]
            cont_path = list(continuationContentPath)  # type: ignore[arg-type]
            key_path = list(continuationKeyPath)  # type: ignore[arg-type]
            fb_path = list(fallbackContentPath)  # type: ignore[arg-type]

            if not self.continuationKey:
                responseContent = self._getValue(parsed_data, c_path)  # type: ignore[arg-type]
            else:
                responseContent = self._getValue(parsed_data, cont_path)  # type: ignore[arg-type]

            if responseContent and isinstance(responseContent, list):
                for element in responseContent:
                    if isinstance(element, dict):
                        if itemSectionKey in element:
                            self.responseSource = self._getValue(
                                element, [itemSectionKey, "contents"]
                            )
                        if continuationItemKey in element:
                            self.continuationKey = self._getValue(
                                element,
                                key_path,  # type: ignore[arg-type]
                            )
            else:
                self.responseSource = self._getValue(parsed_data, fb_path)  # type: ignore[arg-type]
                if self.responseSource and isinstance(self.responseSource, list):
                    self.continuationKey = self._getValue(
                        self.responseSource[-1],
                        key_path,  # type: ignore[arg-type]
                    )
                else:
                    self.continuationKey = None
        except Exception as e:
            logger.error(
                "Could not parse YouTube response in RequestHandler", exc_info=True
            )
            raise Exception("ERROR: Could not parse YouTube response.") from e
