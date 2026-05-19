from typing import Union, List, Any


def getValue(source: Any, path: List[Union[str, int, None]]) -> Any:
    """
    Safely navigates a nested dictionary/list structure.
    """
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


def getVideoId(video_link: str) -> str:
    if "youtu.be" in video_link:
        if video_link[-1] == "/":
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
