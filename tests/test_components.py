import pytest
from py_yt.core.browse import BrowseCore
from py_yt.core.recommendations import RelatedVideosCore
from py_yt.core.transcript import TranscriptCore
from py_yt.core.video import VideoCore
from py_yt import Suggestions


def test_browse_core_request_body():
    browse = BrowseCore("FEwhat_to_watch")
    browse._getRequestBody()
    assert browse.data["context"]["client"]["clientName"] == "MWEB"
    assert browse.data["context"]["client"]["clientVersion"] == "2.20251021.01.00"


def test_related_videos_core_request_body():
    rel = RelatedVideosCore("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    rel._getRequestBody()
    assert rel.data["context"]["client"]["clientName"] == "MWEB"
    assert rel.data["context"]["client"]["clientVersion"] == "2.20251021.01.00"
    assert rel.data["videoId"] == "dQw4w9WgXcQ"


def test_video_core_prepare_request():
    vc = VideoCore(
        video_link="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        component_mode="getInfo",
        result_mode=1,
        timeout=10,
        enable_html=False,
    )
    vc.prepare_innertube_request()
    assert vc.data["context"]["client"]["clientVersion"] == "2.20251021.01.00"


@pytest.mark.asyncio
async def test_suggestions():
    res = await Suggestions.get("python", language="en", region="US", mode=1)
    assert "result" in res
    assert isinstance(res["result"], list)
    assert len(res["result"]) > 0
