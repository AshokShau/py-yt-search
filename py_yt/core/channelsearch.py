import copy
import json
from typing import Union
from urllib.parse import urlencode

from py_yt.core.constants import requestPayload, searchKey, ResultMode
from py_yt.core.requests import RequestCore
from py_yt.handlers.componenthandler import ComponentHandler


class ChannelSearchCore(RequestCore, ComponentHandler):
    response = None
    responseSource = None
    resultComponents = []

    def __init__(self, query: str, language: str, region: str, search_preferences: str, browse_id: str, timeout: int):
        super().__init__()
        self.query = query
        self.language = language
        self.region = region
        self.browseId = browse_id
        self.searchPreferences = search_preferences
        self.continuationKey = None
        self.timeout = timeout

    async def next(self):
        await self._asyncRequest()
        self._parseChannelSearchSource()
        self.response = self._getChannelSearchComponent(self.response)
        return self.response

    def _parseChannelSearchSource(self) -> None:
        try:
            last_tab = self.response["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][-1]
            if 'expandableTabRenderer' in last_tab:
                self.response = last_tab["expandableTabRenderer"]["content"]["sectionListRenderer"]["contents"]
            else:
                tab_renderer = last_tab["tabRenderer"]
                if 'content' in tab_renderer:
                    self.response = tab_renderer["content"]["sectionListRenderer"]["contents"]
                else:
                    self.response = []
        except:
            raise Exception('ERROR: Could not parse YouTube response.')

    def _getRequestBody(self):
        requestBody = copy.deepcopy(requestPayload)
        requestBody['query'] = self.query
        requestBody['client'] = {
            'hl': self.language,
            'gl': self.region,
        }
        requestBody['params'] = self.searchPreferences
        requestBody['browseId'] = self.browseId
        self.url = 'https://www.youtube.com/youtubei/v1/browse' + '?' + urlencode({
            'key': searchKey,
        })
        self.data = requestBody

    async def _asyncRequest(self) -> None:
        self._getRequestBody()

        request = await self.asyncPostRequest()
        try:
            self.response = request.json()
        except:
            raise Exception('ERROR: Could not make request.')

    def result(self, mode: int = ResultMode.dict) -> Union[str, dict]:
        """Returns the search result.
        Args:
            mode (int, optional): Sets the type of result. Defaults to ResultMode.dict.
        Returns:
            Union[str, dict]: Returns JSON or dictionary.
        """
        if mode == ResultMode.json:
            return json.dumps({'result': self.response}, indent=4)
        elif mode == ResultMode.dict:
            return {'result': self.response}
