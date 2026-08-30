import pytest
from py_yt.core.browse import BrowseCore
from py_yt.core.componenthandler import (
    build_channel_url,
    build_playlist_url,
    build_watch_url,
    get_value,
    get_video_id,
)
from py_yt.core.recommendations import RelatedVideosCore
from py_yt.core.video import VideoCore
from py_yt import Suggestions, Video, Playlist, Recommendations


def test_component_helpers():
    data = {"a": {"b": [10, 20]}}
    assert get_value(data, ["a", "b", 1]) == 20
    assert get_value(data, ["a", "c"]) is None

    assert get_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert get_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert get_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    assert build_watch_url("dQw4w9WgXcQ") == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert build_channel_url("UC123") == "https://www.youtube.com/channel/UC123"
    assert build_playlist_url("PL123") == "https://www.youtube.com/playlist?list=PL123"


def test_browse_core_request_body():
    browse = BrowseCore("FEwhat_to_watch")
    browse._get_request_body()
    assert browse.data["context"]["client"]["clientName"] == "MWEB"
    assert browse.data["context"]["client"]["clientVersion"] == "2.20260821.00.00"


def test_related_videos_core_request_body():
    rel = RelatedVideosCore("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    rel._get_request_body()
    assert rel.data["context"]["client"]["clientName"] == "MWEB"
    assert rel.data["context"]["client"]["clientVersion"] == "2.20260821.00.00"
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
    assert vc.data["context"]["client"]["clientVersion"] == "2.20260820.08.00"


@pytest.mark.asyncio
async def test_suggestions():
    res = await Suggestions.get("python", language="en", region="US", mode=1)
    assert "result" in res
    assert isinstance(res["result"], list)
    assert len(res["result"]) > 0
