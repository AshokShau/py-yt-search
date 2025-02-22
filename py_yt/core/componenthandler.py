from typing import Union


def getValue(source: dict, path: list[str]) -> Union[str, int, dict, None]:
    value = source
    for key in path:
        if type(key) is str:
            if key in value.keys():
                value = value[key]
            else:
                value = None
                break
        elif type(key) is int:
            if len(value) != 0:
                value = value[key]
            else:
                value = None
                break
    return value


def getVideoId(video_link: str) -> str:
    if 'youtu.be' in video_link:
        if video_link[-1] == '/':
            return video_link.split('/')[-2]
        return video_link.split('/')[-1]
    elif 'youtube.com' in video_link:
        if '&' not in video_link:
            return video_link[video_link.index('v=') + 2:]
        return video_link[video_link.index('v=') + 2: video_link.index('&')]
    else:
        return video_link
