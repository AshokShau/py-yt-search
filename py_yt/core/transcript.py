import logging
from typing import Any, Dict, List, Optional
import aiohttp

from py_yt.core.componenthandler import get_value, get_video_id
from py_yt.core.requests import RequestCore

logger = logging.getLogger(__name__)


class TranscriptCore(RequestCore):
    def __init__(
        self,
        videoLink: str,
        key: Optional[str] = None,
        proxy: Optional[str] = None,
    ) -> None:
        super().__init__(proxy=proxy)
        self.videoLink: str = videoLink
        self.key: str = key or ""
        self.result: Dict[str, Any] = {"segments": [], "languages": []}

    def prepare_params_request(self) -> None:
        self.url = self._build_url("next", {"prettyPrint": "false"})
        self.data = self._build_payload(
            videoId=get_video_id(self.videoLink),
        )

    async def extract_continuation_key(self, r: aiohttp.ClientResponse) -> bool:
        try:
            j = await r.json()
        except Exception:
            self.result = {"segments": [], "languages": []}
            return True
        panels = get_value(j, ["engagementPanels"])
        if not panels or not isinstance(panels, list):
            self.result = {"segments": [], "languages": []}
            return True
        key = ""
        for panel in panels:
            if not isinstance(panel, dict):
                continue
            section = panel.get("engagementPanelSectionListRenderer", {})
            if (
                get_value(section, ["targetId"])
                == "engagement-panel-searchable-transcript"
            ):
                key = get_value(
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

    def prepare_transcript_request(self) -> None:
        self.url = self._build_url("get_transcript", {"prettyPrint": "false"})
        self.data = self._build_payload(
            params=self.key,
        )

    def extract_transcript(self) -> None:
        response = self.data if isinstance(self.data, dict) else {}
        transcripts = get_value(
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
                seg_renderer = get_value(segment, ["transcriptSegmentRenderer"])
                if seg_renderer and isinstance(seg_renderer, dict):
                    j = {
                        "startMs": get_value(seg_renderer, ["startMs"]),
                        "endMs": get_value(seg_renderer, ["endMs"]),
                        "text": get_value(seg_renderer, ["snippet", "runs", 0, "text"]),
                        "startTime": get_value(
                            seg_renderer, ["startTimeText", "simpleText"]
                        ),
                    }
                    segments.append(j)
        langs = get_value(
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
                        "params": get_value(
                            language,
                            ["continuation", "reloadContinuationData", "continuation"],
                        ),
                        "selected": get_value(language, ["selected"]),
                        "title": get_value(language, ["title"]),
                    }
                    languages.append(j)
        self.result = {"segments": segments, "languages": languages}

    async def create(self) -> None:
        if not self.key:
            self.prepare_params_request()
            r = await self.post_request()
            if not r:
                return
            end = await self.extract_continuation_key(r)
            if end:
                return
        self.prepare_transcript_request()
        response = await self.post_request()
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
