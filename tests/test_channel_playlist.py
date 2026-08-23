from unittest.mock import AsyncMock, patch
import pytest
from py_yt.core.channelsearch import ChannelSearchCore
from py_yt.core.hashtag import HashtagCore
from py_yt.core.playlist import PlaylistCore
from py_yt.exceptions import PyYTSearchError, ParsingError, RequestError


def test_custom_exceptions():
    err = PyYTSearchError("test error")
    assert isinstance(err, Exception)
    p_err = ParsingError("parse error")
    assert isinstance(p_err, PyYTSearchError)
    r_err = RequestError("req error")
    assert isinstance(r_err, PyYTSearchError)


def test_channel_search_request_body():
    cs = ChannelSearchCore(
        query="python",
        language="en",
        region="US",
        search_preferences="",
        browse_id="UC123456",
        timeout=10,
    )
    cs._getRequestBody()
    assert cs.url is not None
    assert cs.data["browseId"] == "UC123456"
    assert cs.data["query"] == "python"


@pytest.mark.asyncio
async def test_channel_search_empty_response():
    cs = ChannelSearchCore(
        query="python",
        language="en",
        region="US",
        search_preferences="",
        browse_id="UC123456",
        timeout=10,
    )
    cs.response = {}
    cs._parseChannelSearchSource()
    assert cs.response == []


def test_playlist_prepare_first_request_standard():
    pl = PlaylistCore(
        playlist_link="https://www.youtube.com/playlist?list=PL123456",
        componentMode="",
        result_mode=1,
        timeout=10,
    )
    pl.prepare_first_request()
    assert pl.data["browseId"] == "VLPL123456"


def test_playlist_prepare_first_request_mix():
    pl = PlaylistCore(
        playlist_link="https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RD123456",
        componentMode="",
        result_mode=1,
        timeout=10,
    )
    pl.prepare_first_request()
    assert pl.data["playlistId"] == "RD123456"
    assert pl.data["videoId"] == "dQw4w9WgXcQ"


@pytest.mark.asyncio
async def test_hashtag_params_fetch_failure():
    ht = HashtagCore("python", limit=10, language="en", region="US", timeout=5)
    with patch.object(ht, "postRequest", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = None
        with pytest.raises(Exception, match="Could not make request"):
            await ht._getParams()
