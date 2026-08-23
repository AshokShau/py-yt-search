import pytest
from py_yt import VideosSearch, Search
from py_yt.core.search import SearchCore


@pytest.mark.asyncio
async def test_videos_search_live():
    search = VideosSearch("python tutorial", limit=2)
    res = await search.next()
    assert "result" in res
    assert len(res["result"]) > 0
    first_item = res["result"][0]
    assert "id" in first_item
    assert "title" in first_item


@pytest.mark.asyncio
async def test_search_all_live():
    search = Search("python programming", limit=2)
    res = await search.next()
    assert "result" in res
    assert len(res["result"]) > 0


def test_search_core_video_id_query_extraction():
    search = SearchCore(
        query="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        limit=5,
        language="en",
        region="US",
        searchPreferences="test",
        timeout=10,
    )
    search._getRequestBody()
    assert search.data["query"] == "dQw4w9WgXcQ"
    # When query is a direct video link, params should not be set
    assert "params" not in search.data


def test_search_core_special_characters_query():
    search = SearchCore(
        query="Python 3.12 & Asyncio 🚀 #coding",
        limit=5,
        language="en",
        region="US",
        searchPreferences="",
        timeout=10,
    )
    search._getRequestBody()
    assert search.data["query"] == "Python 3.12 & Asyncio 🚀 #coding"
