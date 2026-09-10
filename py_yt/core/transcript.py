import html as html_lib
import logging
import re
from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET
import aiohttp

from py_yt.core.componenthandler import get_value, get_video_id
from py_yt.core.requests import RequestCore
from py_yt.core.session import get_session

logger = logging.getLogger(__name__)


class TranscriptCore(RequestCore):
    def __init__(
        self,
        video_link: str,
        key: Optional[str] = None,
        timeout: float = 7.0,
        max_retries: int = 2,
        proxy: Optional[str] = None,
        visitor_data: Optional[str] = None,
        po_token: Optional[str] = None,
        po_token_verifier: Optional[Any] = None,
    ) -> None:
        super().__init__(
            timeout=timeout,
            max_retries=max_retries,
            proxy=proxy,
            visitor_data=visitor_data,
            po_token=po_token,
            po_token_verifier=po_token_verifier,
        )
        self.video_link: str = video_link
        self.videoLink: str = video_link
        self.key: str = key or ""
        self.result: Dict[str, Any] = {"segments": [], "languages": []}

    def prepare_params_request(self) -> None:
        self.url = self._build_url("next", {"prettyPrint": "false"})
        self.data = self._build_payload(
            videoId=get_video_id(self.video_link),
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

    async def fetch_player_captions(self) -> bool:
        video_id = get_video_id(self.video_link)
        if not video_id:
            return False

        session = await get_session()
        url = self._build_url("player", {"prettyPrint": "false"})
        payload = {
            "context": {
                "client": {
                    "hl": "en",
                    "gl": "US",
                    "clientName": "ANDROID",
                    "clientVersion": "20.10.38",
                }
            },
            "videoId": video_id,
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "X-YouTube-Client-Name": "3",
            "X-YouTube-Client-Version": "20.10.38",
            "Content-Type": "application/json",
        }
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        try:
            async with session.post(
                url, json=payload, headers=headers, proxy=self.proxy_url, timeout=timeout
            ) as response:
                if response.status != 200:
                    return False
                player_json = await response.json()
        except Exception:
            return False

        tracklist = get_value(player_json, ["captions", "playerCaptionsTracklistRenderer"]) or get_value(player_json, ["playerCaptionsTracklistRenderer"])
        tracks = get_value(tracklist, ["captionTracks"]) if isinstance(tracklist, dict) else None

        if not tracks or not isinstance(tracks, list):
            return False

        languages: List[Dict[str, Any]] = []
        for t in tracks:
            if isinstance(t, dict):
                name = get_value(t, ["name", "simpleText"]) or t.get("languageCode", "")
                languages.append({
                    "languageCode": t.get("languageCode"),
                    "name": name,
                    "title": name,
                    "isAutoGenerated": t.get("kind") == "asr",
                    "baseUrl": t.get("baseUrl") or t.get("url"),
                })

        base_url = tracks[0].get("baseUrl") or tracks[0].get("url")
        if not base_url or not isinstance(base_url, str):
            self.result = {"segments": [], "languages": languages}
            return True

        xml_url = re.sub(r"&fmt=[^&]+", "", base_url)
        session = await get_session()
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        segments: List[Dict[str, Any]] = []
        try:
            async with session.get(xml_url, proxy=self.proxy_url, timeout=timeout) as tr_resp:
                if tr_resp.status == 200:
                    xml_text = await tr_resp.text()
                    try:
                        root = ET.fromstring(xml_text)
                        for node in root.findall(".//text"):
                            start = float(node.attrib.get("start", 0))
                            dur = float(node.attrib.get("dur", 0))
                            text = html_lib.unescape(node.text or "").strip()
                            if text:
                                start_sec = int(start)
                                segments.append({
                                    "startMs": str(int(start * 1000)),
                                    "endMs": str(int((start + dur) * 1000)),
                                    "text": text,
                                    "startTime": f"{start_sec // 60}:{start_sec % 60:02d}",
                                })
                    except Exception:
                        pass
        except Exception as e:
            logger.debug(f"Failed to fetch timedtext XML: {e}")

        self.result = {"segments": segments, "languages": languages}
        return len(segments) > 0

    async def create(self) -> None:
        fetched = await self.fetch_player_captions()
        if fetched:
            return

        if not self.key:
            self.prepare_params_request()
            r = await self.post_request(client_profiles=["WEB"], exc_info=False)
            if not r:
                return
            end = await self.extract_continuation_key(r)
            if end:
                return
        self.prepare_transcript_request()
        response = await self.post_request(client_profiles=["WEB"], exc_info=False)
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
