import copy
import json
from typing import Any, Dict, Optional, Union
from urllib.parse import parse_qs, urlparse

from py_yt.core.componenthandler import (
    build_channel_url,
    build_watch_url,
    get_value,
    get_video_id,
)
from py_yt.core.constants import ResultMode
from py_yt.core.requests import RequestCore

CLIENTS: Dict[str, Dict[str, Any]] = {
    "MWEB": {
        "context": {
            "client": {"clientName": "WEB", "clientVersion": "2.20260820.08.00"}
        },
        "api_key": "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
    },
    "ANDROID": {
        "context": {
            "client": {"clientName": "WEB", "clientVersion": "2.20260820.08.00"}
        },
        "api_key": "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
    },
    "ANDROID_EMBED": {
        "context": {
            "client": {
                "clientName": "WEB",
                "clientVersion": "2.20260820.08.00",
                "clientScreen": "EMBED",
            }
        },
        "api_key": "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
    },
    "TV_EMBED": {
        "context": {
            "client": {
                "clientName": "TVHTML5_SIMPLY_EMBEDDED_PLAYER",
                "clientVersion": "2.0",
            },
            "thirdParty": {
                "embedUrl": "https://www.youtube.com/",
            },
        },
        "api_key": "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
    },
}


def _get_cleaned_url(video_link: str) -> str:
    """Cleans the YouTube video link by removing any extra parameters, ensuring only the video ID is present."""
    parsed_url = urlparse(video_link)
    video_id = parse_qs(parsed_url.query).get("v")
    if video_id:
        return f"https://www.youtube.com/watch?v={video_id[0]}"
    return video_link


class VideoCore(RequestCore):
    response: Optional[str] = None
    responseSource: Optional[Dict[str, Any]] = None
    HTMLresponseSource: Optional[Dict[str, Any]] = None
    result: Optional[Union[Dict[str, Any], str]] = None
    _video_component: Dict[str, Any] = {}

    def __init__(
        self,
        video_link: str,
        component_mode: Optional[str],
        result_mode: int,
        timeout: float,
        enable_html: bool,
        overrided_client: str = "ANDROID",
        proxy: Optional[str] = None,
    ) -> None:
        super().__init__(timeout=timeout, proxy=proxy)
        self.timeout: float = timeout
        self.resultMode: int = result_mode
        self.componentMode: Optional[str] = component_mode
        self.videoLink: str = _get_cleaned_url(video_link)
        self.enableHTML: bool = enable_html
        self.overridedClient: str = overrided_client

    def post_request_processing(self) -> None:
        if self.response is not None:
            self._parse_source()
        self._get_video_component(self.componentMode)
        self.result = self._video_component

    def prepare_innertube_request(self) -> None:
        self.url = self._build_url(
            "player",
            {
                "contentCheckOk": "true",
                "racyCheckOk": "true",
                "videoId": get_video_id(self.videoLink),
            },
        )
        self.data = copy.deepcopy(CLIENTS.get(self.overridedClient, CLIENTS["ANDROID"]))

    async def create(self) -> None:
        self.prepare_innertube_request()
        response = await self.post_request()
        if response is None:
            video_link = getattr(self, "videoLink", None)
            request_params = getattr(self, "data", None)
            raise Exception(
                f"The request returned an empty response. "
                f"Video link: {video_link}, Request parameters: {request_params}"
            )

        self.response = await response.text()
        if response.status == 200:
            self.post_request_processing()
        else:
            raise Exception("ERROR: Invalid status code.")

    def prepare_html_request(self) -> None:
        self.url = self._build_url(
            "player",
            {
                "contentCheckOk": "true",
                "racyCheckOk": "true",
                "videoId": get_video_id(self.videoLink),
            },
        )
        self.data = CLIENTS["MWEB"]

    async def html_create(self) -> None:
        self.prepare_html_request()
        response = await self.post_request()
        if response is None:
            raise Exception("ERROR: Could not fetch HTML response.")
        self.HTMLresponseSource = await response.json()

    def _parse_source(self) -> None:
        try:
            self.responseSource = json.loads(self.response or "{}")
        except Exception as e:
            raise Exception("ERROR: Could not parse YouTube response.") from e

    def _result(self, mode: int) -> Union[Dict[str, Any], str]:
        if mode == ResultMode.dict:
            return self._video_component
        return json.dumps(self._video_component, indent=4)

    def _get_video_component(self, mode: Optional[str]) -> None:
        videoComponent: Dict[str, Any] = {}
        if mode in ["getInfo", None]:
            responseSource = self.responseSource
            if self.enableHTML and self.HTMLresponseSource:
                responseSource = self.HTMLresponseSource
            vid: Optional[str] = get_value(responseSource, ["videoDetails", "videoId"])
            cid: Optional[str] = get_value(responseSource, ["videoDetails", "channelId"])
            component: Dict[str, Any] = {
                "id": vid,
                "title": get_value(responseSource, ["videoDetails", "title"]),
                "duration": {
                    "secondsText": get_value(
                        responseSource, ["videoDetails", "lengthSeconds"]
                    ),
                },
                "viewCount": {
                    "text": get_value(responseSource, ["videoDetails", "viewCount"])
                },
                "thumbnails": get_value(
                    responseSource, ["videoDetails", "thumbnail", "thumbnails"]
                ),
                "description": get_value(
                    responseSource, ["videoDetails", "shortDescription"]
                ),
                "channel": {
                    "name": get_value(responseSource, ["videoDetails", "author"]),
                    "id": cid,
                    "link": build_channel_url(cid),
                },
                "allowRatings": get_value(
                    responseSource, ["videoDetails", "allowRatings"]
                ),
                "averageRating": get_value(
                    responseSource, ["videoDetails", "averageRating"]
                ),
                "keywords": get_value(responseSource, ["videoDetails", "keywords"]),
                "isLiveContent": get_value(
                    responseSource, ["videoDetails", "isLiveContent"]
                ),
                "publishDate": get_value(
                    responseSource,
                    ["microformat", "playerMicroformatRenderer", "publishDate"],
                ),
                "uploadDate": get_value(
                    responseSource,
                    ["microformat", "playerMicroformatRenderer", "uploadDate"],
                ),
                "isFamilySafe": get_value(
                    responseSource,
                    ["microformat", "playerMicroformatRenderer", "isFamilySafe"],
                ),
                "category": get_value(
                    responseSource,
                    ["microformat", "playerMicroformatRenderer", "category"],
                ),
                "link": build_watch_url(vid),
            }
            component["isLiveNow"] = bool(
                component["isLiveContent"]
                and component["duration"]["secondsText"] == "0"
            )
            videoComponent.update(component)

        if mode in ["getFormats", None]:
            videoComponent.update(
                {"streamingData": get_value(self.responseSource, ["streamingData"])}
            )

        if self.enableHTML and self.HTMLresponseSource:
            videoComponent["publishDate"] = get_value(
                self.HTMLresponseSource,
                ["microformat", "playerMicroformatRenderer", "publishDate"],
            )
            videoComponent["uploadDate"] = get_value(
                self.HTMLresponseSource,
                ["microformat", "playerMicroformatRenderer", "uploadDate"],
            )

        self._video_component = videoComponent
