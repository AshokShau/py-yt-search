import pytest
from py_yt.core.requests import RequestCore
from py_yt.core.search import SearchCore
from py_yt.core.channelsearch import ChannelSearchCore
from py_yt.core.constants import userAgent, requestPayload


def test_request_core_headers_default():
    req = RequestCore()
    headers = req._get_headers()
    assert headers["User-Agent"] == userAgent
    assert headers["Origin"] == "https://www.youtube.com"
    assert headers["Referer"] == "https://www.youtube.com/"
    assert headers["Accept-Language"] == "en-US,en;q=0.9"


def test_request_core_headers_with_client_data():
    req = RequestCore()
    req.data = {
        "context": {
            "client": {
                "clientName": "MWEB",
                "clientVersion": "2.20251021.01.00",
            }
        }
    }
    headers = req._get_headers()
    assert headers["X-YouTube-Client-Name"] == "2"
    assert headers["X-YouTube-Client-Version"] == "2.20251021.01.00"


def test_search_core_request_body():
    search = SearchCore(
        query="python",
        limit=5,
        language="en",
        region="US",
        searchPreferences="",
        timeout=10,
    )
    search._getRequestBody()
    assert "client" not in search.data  # Ensure no top-level client key
    assert search.data["context"]["client"]["hl"] == "en"
    assert search.data["context"]["client"]["gl"] == "US"
    assert search.data["context"]["client"]["clientVersion"] == "2.20251021.01.00"


def test_channel_search_core_request_body():
    cs = ChannelSearchCore(
        query="python",
        language="en",
        region="US",
        search_preferences="",
        browse_id="UC123456",
        timeout=10,
    )
    cs._getRequestBody()
    assert "client" not in cs.data  # Ensure no top-level client key
    assert cs.data["context"]["client"]["hl"] == "en"
    assert cs.data["context"]["client"]["gl"] == "US"
