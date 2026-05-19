import copy
import json
from urllib.parse import urlencode

from py_yt.core.constants import (
    requestPayload,
    searchKey,
    contentPath,
    itemSectionKey,
    continuationItemKey,
    continuationKeyPath,
    fallbackContentPath,
    continuationContentPath,
)
from py_yt.handlers.componenthandler import ComponentHandler


class RequestHandler(ComponentHandler):
    def _parseSource(self) -> None:
        try:
            if not self.continuationKey:
                responseContent = self._getValue(json.loads(self.response), contentPath)
            else:
                responseContent = self._getValue(
                    json.loads(self.response), continuationContentPath
                )
            if responseContent:
                for element in responseContent:
                    if itemSectionKey in element.keys():
                        self.responseSource = self._getValue(
                            element, [itemSectionKey, "contents"]
                        )
                    if continuationItemKey in element.keys():
                        self.continuationKey = self._getValue(
                            element, continuationKeyPath
                        )
            else:
                self.responseSource = self._getValue(
                    json.loads(self.response), fallbackContentPath
                )
                if self.responseSource:
                    self.continuationKey = self._getValue(
                        self.responseSource[-1], continuationKeyPath
                    )
                else:
                    self.continuationKey = None
        except:
            raise Exception("ERROR: Could not parse YouTube response.")
