from unittest.mock import AsyncMock, patch
import pytest
from py_yt.core.requests import RequestCore
from py_yt.core.search import SearchCore
from py_yt.core.channelsearch import ChannelSearchCore
from py_yt.core.constants import userAgent, requestPayload, CLIENT_PROFILES
from py_yt.core.session import (
    set_session_visitor_data,
    get_session_visitor_data,
    set_session_po_token,
    get_session_po_token,
    set_session_po_token_verifier,
    get_session_po_token_verifier,
)


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


@pytest.mark.asyncio
async def test_request_core_po_token_and_visitor_data():
    req = RequestCore(
        visitor_data="CgVTEST123",
        po_token="MnTESTPO123",
    )
    req.data = {"context": {"client": {}}}
    headers = req._prepare_request_for_profile("WEB")
    assert headers["X-Goog-Visitor-Id"] == "CgVTEST123"
    assert req.data["context"]["client"]["visitorData"] == "CgVTEST123"
    assert req.data["context"]["client"]["serviceIntegrityDimensions"]["poToken"] == "MnTESTPO123"


@pytest.mark.asyncio
async def test_resolve_tokens_with_verifier():
    def dummy_verifier():
        return ("CgVTESTVISITOR", "MnTESTPOTOKEN")

    req = RequestCore(po_token_verifier=dummy_verifier)
    vd, po = await req._resolve_tokens()
    assert vd == "CgVTESTVISITOR"
    assert po == "MnTESTPOTOKEN"
    assert req.visitor_data == "CgVTESTVISITOR"
    assert req.po_token == "MnTESTPOTOKEN"


@pytest.mark.asyncio
async def test_automatic_visitor_data_fetch():
    req = RequestCore()
    with patch.object(req, "_fetch_automatic_visitor_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = "CgtMOCK_VISITOR_DATA"
        vd = await req._fetch_automatic_visitor_data()
        assert vd == "CgtMOCK_VISITOR_DATA"


def test_session_tokens():
    set_session_visitor_data("VISITOR_SESS")
    assert get_session_visitor_data() == "VISITOR_SESS"

    set_session_po_token("PO_SESS")
    assert get_session_po_token() == "PO_SESS"

    v_fn = lambda: "PO"
    set_session_po_token_verifier(v_fn)
    assert get_session_po_token_verifier() == v_fn


def test_client_profiles_rotation():
    req = RequestCore()
    req.data = {"context": {"client": {}}}

    h_web = req._prepare_request_for_profile("WEB")
    assert h_web["X-YouTube-Client-Name"] == "1"

    h_mweb = req._prepare_request_for_profile("MWEB")
    assert h_mweb["X-YouTube-Client-Name"] == "2"

    h_vr = req._prepare_request_for_profile("ANDROID_VR")
    assert h_vr["X-YouTube-Client-Name"] == "93"
