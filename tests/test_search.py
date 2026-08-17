import pytest
from py_yt import VideosSearch, Search


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
