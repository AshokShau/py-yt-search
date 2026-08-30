import math
import re
from datetime import datetime, timezone
from typing import Any, Dict, List


def parse_view_count(val: Any) -> int:
    """Safely extracts integer view count from string, dict, or int."""
    if val is None:
        return 0
    if isinstance(val, (int, float)):
        return max(0, int(val))
    if isinstance(val, dict):
        text = val.get("text") or val.get("short") or ""
        return parse_view_count(text)

    s = str(val).strip().lower()
    if not s or s == "none":
        return 0

    # Handle short formats like '1.2M views', '500K views', '2.5B views'
    m_short = re.search(r"([\d.]+)\s*([kmb])", s)
    if m_short:
        num = float(m_short.group(1))
        unit = m_short.group(2)
        multiplier = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}.get(unit, 1)
        return max(0, int(num * multiplier))

    # Handle formatted numbers like '162,235,006 views'
    digits = re.sub(r"[^\d]", "", s)
    if digits:
        return max(0, int(digits))
    return 0


def parse_age_in_hours(published_val: Any, publish_date_val: Any = None) -> float:
    """Safely calculates age in hours from publish timestamp or relative string like '2 hours ago'."""
    # First try ISO publish_date
    for date_str in [publish_date_val, published_val]:
        if isinstance(date_str, str) and ("T" in date_str or "-" in date_str):
            try:
                # Handle ISO 8601 strings
                dt_str = date_str.replace("Z", "+00:00")
                dt = datetime.fromisoformat(dt_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                diff_hours = (now - dt).total_seconds() / 3600.0
                if diff_hours >= 0:
                    return diff_hours
            except (ValueError, TypeError):
                pass

    # Next, parse relative publishedTime strings (e.g. '5 minutes ago', '2 hours ago', '3 days ago')
    s = str(published_val or "").strip().lower()
    if s:
        m = re.search(r"(\d+)\s*(minute|min|hour|hr|day|week|month|year)", s)
        if m:
            val = float(m.group(1))
            unit = m.group(2)
            if "min" in unit:
                hours = val / 60.0
            elif "hour" in unit or "hr" in unit:
                hours = val
            elif "day" in unit:
                hours = val * 24.0
            elif "week" in unit:
                hours = val * 24.0 * 7.0
            elif "month" in unit:
                hours = val * 24.0 * 30.4375
            elif "year" in unit:
                hours = val * 24.0 * 365.25
            else:
                hours = 24.0
            return max(0.001, hours)

    # Default fallback: 24 hours if unknown
    return 24.0


class HypeHint:
    """HYPE HINT calculates momentum and hype metrics for YouTube videos."""

    @staticmethod
    def calculate_score(
        view_count: Any,
        published_time: Any = None,
        publish_date: Any = None,
        subscriber_count: Any = None,
        like_count: Any = None,
    ) -> float:
        """Calculates a deterministic hype score bounded between 0.0 and 100.0.

        Formula components:
        1. View Velocity (views/hour) log-scaled.
        2. Recency Boost for videos published recently (< 72 hours).
        3. View Scale log factor so high overall view counts provide momentum baseline.
        4. Bounded output between 0.0 and 100.0.
        """
        views = parse_view_count(view_count)
        if views <= 0:
            return 0.0

        age_hours = parse_age_in_hours(published_time, publish_date)
        # Floor age at 0.25h (15 min) to avoid division-by-zero or insane velocity spikes for 1-minute-old videos
        effective_age = max(0.25, age_hours)

        velocity = views / effective_age

        # Velocity score using log scale (e.g. 10 views/hr -> log10=1, 100k views/hr -> log10=5)
        log_velocity = math.log10(velocity + 1.0)
        velocity_score = log_velocity * 18.0

        # View scale bonus (log10 views)
        log_views = math.log10(views + 1.0)
        scale_bonus = log_views * 3.5

        # Recency boost multiplier: smooth exponential decay based on age
        # Full boost for <= 24h, gradually decaying towards 1.0 after 7 days (168h)
        recency_factor = math.exp(-effective_age / 120.0)
        recency_bonus = recency_factor * 15.0

        raw_score = velocity_score + scale_bonus + recency_bonus

        # Bounded between 0.0 and 100.0 rounded to 2 decimal places
        final_score = min(100.0, max(0.0, raw_score))
        return round(final_score, 2)

    @classmethod
    def get_hype_level(cls, score: float) -> str:
        """Returns descriptive hype level category based on score."""
        if score >= 85.0:
            return "Ultra Viral"
        elif score >= 70.0:
            return "High Hype"
        elif score >= 50.0:
            return "Trending"
        elif score >= 30.0:
            return "Moderate"
        elif score > 0.0:
            return "Low Hype"
        return "No Hype"

    @classmethod
    def analyze_video(cls, video: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes a video dictionary and returns hype details dictionary."""
        if not isinstance(video, dict):
            return {
                "score": 0.0,
                "level": "No Hype",
                "view_count": 0,
                "age_hours": 24.0,
                "velocity_views_per_hour": 0.0,
            }

        view_count = video.get("viewCount")
        if view_count is None:
            view_count = video.get("views")

        published_time = video.get("publishedTime") or video.get("published")
        publish_date = video.get("publishDate") or video.get("uploadDate")

        views_int = parse_view_count(view_count)
        age_hrs = parse_age_in_hours(published_time, publish_date)
        score = cls.calculate_score(view_count, published_time, publish_date)
        level = cls.get_hype_level(score)

        return {
            "score": score,
            "level": level,
            "view_count": views_int,
            "age_hours": round(age_hrs, 2),
            "velocity_views_per_hour": round(views_int / max(0.25, age_hrs), 2),
        }

    @classmethod
    def rank(
        cls, videos: List[Dict[str, Any]], inplace: bool = False
    ) -> List[Dict[str, Any]]:
        """Ranks a list of video dictionaries by hype score descending.

        Attaches 'hype' dictionary containing score, level, and velocity info to each video dict.
        """
        if not videos:
            return []

        processed = []
        for v in videos:
            if isinstance(v, dict):
                item = v if inplace else dict(v)
                hype_data = cls.analyze_video(item)
                item["hype"] = hype_data
                processed.append(item)
            else:
                processed.append(v)

        processed.sort(
            key=lambda x: (
                x.get("hype", {}).get("score", 0.0) if isinstance(x, dict) else 0.0
            ),
            reverse=True,
        )
        return processed
