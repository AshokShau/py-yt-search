import copy
import logging
from typing import Any, Dict, List
from urllib.parse import urlencode

from py_yt.core.componenthandler import getVideoId, getValue
from py_yt.core.constants import searchKey, requestPayload
from py_yt.core.requests import RequestCore

logger = logging.getLogger(__name__)


class TranscriptCore(RequestCore):
    def __init__(
        self, videoLink: str, key: str | None = None, proxy: str | None = None
    ):
        super().__init__(proxy=proxy)
        self.videoLink = videoLink
        self.key = key or ""
        self.result: Dict[str, Any] = {"segments": [], "languages": []}

    def prepare_params_request(self):
        self.url = (
            "https://www.youtube.com/youtubei/v1/next"
            + "?"
            + urlencode({"key": searchKey, "prettyPrint": "false"})
        )
        self.data = copy.deepcopy(requestPayload)
        self.data["videoId"] = getVideoId(self.videoLink)

    async def extract_continuation_key(self, r):
        try:
            j = await r.json()
        except Exception:
            self.result = {"segments": [], "languages": []}
            return True
        panels = getValue(j, ["engagementPanels"])
        if not panels or not isinstance(panels, list):
            self.result = {"segments": [], "languages": []}
            return True
        key = ""
        for panel in panels:
            if not isinstance(panel, dict):
                continue
            section = panel.get("engagementPanelSectionListRenderer", {})
            if (
                getValue(section, ["targetId"])
                == "engagement-panel-searchable-transcript"
            ):
                key = getValue(
                    section,
                    [
                        "content",
                        "continuationItemRenderer",
                        "continuationEndpoint",
                        "getTranscriptEndpoint",
                        "params",
                    ],
                )
        if not key:
            self.result = {"segments": [], "languages": []}
            return True
        self.key = str(key)
        return False

    def prepare_transcript_request(self):
        self.url = (
            "https://www.youtube.com/youtubei/v1/get_transcript"
            + "?"
            + urlencode({"key": searchKey, "prettyPrint": "false"})
        )
        self.data = copy.deepcopy(requestPayload)
        self.data["params"] = self.key

    def extract_transcript(self):
        response = self.data if isinstance(self.data, dict) else {}
        transcripts = getValue(
            response,
            [
                "actions",
                0,
                "updateEngagementPanelAction",
                "content",
                "transcriptRenderer",
                "content",
                "transcriptSearchPanelRenderer",
                "body",
                "transcriptSegmentListRenderer",
                "initialSegments",
            ],
        )
        segments: List[Dict[str, Any]] = []
        languages: List[Dict[str, Any]] = []
        if transcripts and isinstance(transcripts, list):
            for segment in transcripts:
                seg_renderer = getValue(segment, ["transcriptSegmentRenderer"])
                if seg_renderer and isinstance(seg_renderer, dict):
                    j = {
                        "startMs": getValue(seg_renderer, ["startMs"]),
                        "endMs": getValue(seg_renderer, ["endMs"]),
                        "text": getValue(seg_renderer, ["snippet", "runs", 0, "text"]),
                        "startTime": getValue(
                            seg_renderer, ["startTimeText", "simpleText"]
                        ),
                    }
                    segments.append(j)
        langs = getValue(
            response,
            [
                "actions",
                0,
                "updateEngagementPanelAction",
                "content",
                "transcriptRenderer",
                "content",
                "transcriptSearchPanelRenderer",
                "footer",
                "transcriptFooterRenderer",
                "languageMenu",
                "sortFilterSubMenuRenderer",
                "subMenuItems",
            ],
        )
        if langs and isinstance(langs, list):
            for language in langs:
                if isinstance(language, dict):
                    j = {
                        "params": getValue(
                            language,
                            ["continuation", "reloadContinuationData", "continuation"],
                        ),
                        "selected": getValue(language, ["selected"]),
                        "title": getValue(language, ["title"]),
                    }
                    languages.append(j)
        self.result = {"segments": segments, "languages": languages}

    async def create(self):
        if not self.key:
            self.prepare_params_request()
            r = await self.postRequest()
            if not r:
                return
            end = await self.extract_continuation_key(r)
            if end:
                return
        self.prepare_transcript_request()
        response = await self.postRequest()
        if response:
            try:
                self.data = await response.json()
            except Exception:
                logger.error(
                    "Could not parse YouTube response inside extract_transcript.",
                    exc_info=True,
                )
                return
            self.extract_transcript()
