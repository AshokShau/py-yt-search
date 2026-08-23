import json
import logging
from typing import Any, Optional, Sequence, Union

from py_yt.core.constants import (
    contentPath,
    continuationContentPath,
    continuationItemKey,
    continuationKeyPath,
    fallbackContentPath,
    itemSectionKey,
)
from py_yt.handlers.componenthandler import ComponentHandler

logger = logging.getLogger(__name__)


class RequestHandler(ComponentHandler):
    response: Optional[Any] = None
    continuationKey: Optional[str] = None
    responseSource: Optional[Any] = None

    def _parse_source(self) -> None:
        try:
            resp = self.response or ""
            parsed_data = json.loads(resp) if isinstance(resp, str) else (resp or {})
            c_path: Sequence[Union[str, int, None]] = contentPath  # type: ignore[assignment]
            cont_path: Sequence[Union[str, int, None]] = continuationContentPath  # type: ignore[assignment]
            key_path: Sequence[Union[str, int, None]] = continuationKeyPath  # type: ignore[assignment]
            fb_path: Sequence[Union[str, int, None]] = fallbackContentPath  # type: ignore[assignment]

            if not self.continuationKey:
                response_content = self._get_value(parsed_data, c_path)
            else:
                response_content = self._get_value(parsed_data, cont_path)

            if response_content and isinstance(response_content, list):
                for element in response_content:
                    if isinstance(element, dict):
                        if itemSectionKey in element:
                            self.responseSource = self._get_value(
                                element, [itemSectionKey, "contents"]
                            )
                        if continuationItemKey in element:
                            self.continuationKey = self._get_value(
                                element,
                                key_path,
                            )
            else:
                self.responseSource = self._get_value(parsed_data, fb_path)
                if self.responseSource and isinstance(self.responseSource, list):
                    self.continuationKey = self._get_value(
                        self.responseSource[-1],
                        key_path,
                    )
                else:
                    self.continuationKey = None
        except Exception as e:
            logger.error(
                "Could not parse YouTube response in RequestHandler", exc_info=True
            )
            raise Exception("ERROR: Could not parse YouTube response.") from e
