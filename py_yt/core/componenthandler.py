from typing import Any, Optional, Sequence, Union


def get_value(source: Any, path: Sequence[Union[str, int, None]]) -> Any:
    """Safely navigates a nested dictionary/list structure."""
    value = source
    for key in path:
        if key is None:
            return None

        if isinstance(key, str):
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        elif isinstance(key, int):
            if isinstance(value, list) and 0 <= key < len(value):
                value = value[key]
            else:
                return None
        else:
            return None
    return value


def get_video_id(video_link: str) -> str:
    """Extracts a video ID from a YouTube URL or returns the input if already an ID."""
    if "youtu.be" in video_link:
        if video_link.endswith("/"):
            return video_link.split("/")[-2]
        return video_link.split("/")[-1]
    elif "youtube.com" in video_link:
        if "&" not in video_link:
            if "v=" in video_link:
                return video_link[video_link.index("v=") + 2 :]
            return video_link.split("/")[-1]
        return video_link[video_link.index("v=") + 2 : video_link.index("&")]
    else:
        return video_link


def build_watch_url(video_id: Optional[str]) -> Optional[str]:
    """Builds a standard YouTube watch URL from video ID."""
    return f"https://www.youtube.com/watch?v={video_id}" if video_id else None


def build_channel_url(channel_id: Optional[str]) -> Optional[str]:
    """Builds a standard YouTube channel URL from channel ID."""
    return f"https://www.youtube.com/channel/{channel_id}" if channel_id else None


def build_playlist_url(playlist_id: Optional[str]) -> Optional[str]:
    """Builds a standard YouTube playlist URL from playlist ID."""
    return f"https://www.youtube.com/playlist?list={playlist_id}" if playlist_id else None
