import pytest
from py_yt.hype import HypeHint, parse_view_count, parse_age_in_hours


def test_parse_view_count():
    assert parse_view_count(None) == 0
    assert parse_view_count(0) == 0
    assert parse_view_count(1500) == 1500
    assert parse_view_count("162,235,006 views") == 162235006
    assert parse_view_count("1.2M views") == 1200000
    assert parse_view_count("500K views") == 500000
    assert parse_view_count("2.5B views") == 2500000000
    assert parse_view_count({"text": "10,000 views"}) == 10000
    assert parse_view_count("invalid text") == 0


def test_parse_age_in_hours():
    assert parse_age_in_hours("5 minutes ago") == pytest.approx(0.0833, abs=0.01)
    assert parse_age_in_hours("2 hours ago") == 2.0
    assert parse_age_in_hours("3 days ago") == 72.0
    assert parse_age_in_hours("1 month ago") == pytest.approx(730.5, abs=5.0)
    assert parse_age_in_hours(None, None) == 24.0


def test_calculate_score_zero_views():
    assert HypeHint.calculate_score(0) == 0.0
    assert HypeHint.calculate_score(None) == 0.0
    assert HypeHint.calculate_score("0 views") == 0.0


def test_calculate_score_bounds_and_determinism():
    score1 = HypeHint.calculate_score("1,000,000 views", "2 hours ago")
    score2 = HypeHint.calculate_score("1,000,000 views", "2 hours ago")
    assert score1 == score2
    assert 0.0 <= score1 <= 100.0


def test_calculate_score_extreme_inputs():
    # Very large view count (10 Billion)
    large_score = HypeHint.calculate_score(10_000_000_000, "1 hour ago")
    assert 0.0 <= large_score <= 100.0

    # Very new video (0 minutes ago / Floor age)
    new_score = HypeHint.calculate_score("50,000 views", "1 minute ago")
    assert 0.0 <= new_score <= 100.0

    # Very old video (10 years ago)
    old_score = HypeHint.calculate_score("100,000 views", "10 years ago")
    assert 0.0 <= old_score <= 100.0
    assert new_score > old_score


def test_get_hype_level():
    assert HypeHint.get_hype_level(90.0) == "Ultra Viral"
    assert HypeHint.get_hype_level(75.0) == "High Hype"
    assert HypeHint.get_hype_level(55.0) == "Trending"
    assert HypeHint.get_hype_level(35.0) == "Moderate"
    assert HypeHint.get_hype_level(10.0) == "Low Hype"
    assert HypeHint.get_hype_level(0.0) == "No Hype"


def test_analyze_video():
    video = {
        "id": "abc12345",
        "title": "Test Video",
        "viewCount": {"text": "500,000 views"},
        "publishedTime": "3 hours ago",
    }
    analysis = HypeHint.analyze_video(video)
    assert analysis["score"] > 0.0
    assert analysis["view_count"] == 500000
    assert analysis["age_hours"] == 3.0


def test_rank_videos():
    v1 = {
        "title": "Old Video",
        "viewCount": "1,000 views",
        "publishedTime": "5 years ago",
    }
    v2 = {
        "title": "Viral New Video",
        "viewCount": "2,000,000 views",
        "publishedTime": "2 hours ago",
    }
    ranked = HypeHint.rank([v1, v2])
    assert len(ranked) == 2
    assert ranked[0]["title"] == "Viral New Video"
    assert ranked[0]["hype"]["score"] > ranked[1]["hype"]["score"]


def test_rank_edge_cases():
    assert HypeHint.rank([]) == []
    ranked_invalid = HypeHint.rank([None, "invalid", {}])  # type: ignore
    assert len(ranked_invalid) == 3
