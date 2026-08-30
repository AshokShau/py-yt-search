from typing import Any, Dict, List, Union

requestPayload: Dict[str, Any] = {
    "context": {
        "client": {
            "hl": "en",
            "gl": "US",
            "clientName": "WEB",
            "clientVersion": "2.20260820.08.00",
            "newVisitorCookie": True,
        },
        "user": {
            "lockedSafetyMode": False,
        },
    }
}

userAgent: str = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
)

CLIENT_PROFILES: Dict[str, Dict[str, str]] = {
    "WEB": {
        "clientName": "WEB",
        "clientVersion": "2.20260820.08.00",
        "userAgent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        ),
        "clientCode": "1",
    },
    "ANDROID_VR": {
        "clientName": "ANDROID_VR",
        "clientVersion": "1.61.26",
        "userAgent": (
            "Mozilla/5.0 (Linux; Android 12; Quest 3) AppleWebKit/537.36 (KHTML, like Gecko) OculusBrowser/32.0.0.3.17 Chrome/122.0.6261.64 Mobile Safari/537.36"
        ),
        "clientCode": "93",
    },
    "MWEB": {
        "clientName": "MWEB",
        "clientVersion": "2.20260821.00.00",
        "userAgent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"
        ),
        "clientCode": "2",
    },
    "TVHTML5": {
        "clientName": "TVHTML5",
        "clientVersion": "7.20260819.16.00",
        "userAgent": "Mozilla/5.0 (ChromiumStylePlatform) Cobalt/Version",
        "clientCode": "7",
    },
    "ANDROID_TESTSUITE": {
        "clientName": "ANDROID_TESTSUITE",
        "clientVersion": "1.9",
        "userAgent": "com.google.android.apps.youtube.unplugged/1.9 (Linux; U; Android 12)",
        "clientCode": "82",
    },
}

videoElementKey: str = "videoRenderer"
channelElementKey: str = "channelRenderer"
playlistElementKey: str = "playlistRenderer"
shelfElementKey: str = "shelfRenderer"
itemSectionKey: str = "itemSectionRenderer"
continuationItemKey: str = "continuationItemRenderer"
playerResponseKey: str = "playerResponse"
richItemKey: str = "richItemRenderer"
hashtagElementKey: str = "hashtagTileRenderer"
hashtagBrowseKey: str = "FEhashtag"

hashtagVideosPath: List[Union[str, int, None]] = [
    "contents",
    "twoColumnBrowseResultsRenderer",
    "tabs",
    0,
    "tabRenderer",
    "content",
    "richGridRenderer",
    "contents",
]
hashtagContinuationVideosPath: List[Union[str, int, None]] = [
    "onResponseReceivedActions",
    0,
    "appendContinuationItemsAction",
    "continuationItems",
]
searchKey: str = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
contentPath: List[Union[str, int, None]] = [
    "contents",
    "twoColumnSearchResultsRenderer",
    "primaryContents",
    "sectionListRenderer",
    "contents",
]
fallbackContentPath: List[Union[str, int, None]] = [
    "contents",
    "twoColumnSearchResultsRenderer",
    "primaryContents",
    "richGridRenderer",
    "contents",
]
continuationContentPath: List[Union[str, int, None]] = [
    "onResponseReceivedCommands",
    0,
    "appendContinuationItemsAction",
    "continuationItems",
]
continuationKeyPath: List[Union[str, int, None]] = [
    "continuationItemRenderer",
    "continuationEndpoint",
    "continuationCommand",
    "token",
]
playlistInfoPath: List[Union[str, int, None]] = [
    "response",
    "sidebar",
    "playlistSidebarRenderer",
    "items",
]
playlistVideosPath: List[Union[str, int, None]] = [
    "response",
    "contents",
    "twoColumnBrowseResultsRenderer",
    "tabs",
    0,
    "tabRenderer",
    "content",
    "sectionListRenderer",
    "contents",
    0,
    "itemSectionRenderer",
    "contents",
    0,
    "playlistVideoListRenderer",
    "contents",
]
playlistPrimaryInfoKey: str = "playlistSidebarPrimaryInfoRenderer"
playlistSecondaryInfoKey: str = "playlistSidebarSecondaryInfoRenderer"
playlistVideoKey: str = "playlistVideoRenderer"


class ResultMode:
    json: int = 0
    dict: int = 1


class SearchMode:
    videos: str = "EgIQAQ%3D%3D"
    channels: str = "EgIQAg%3D%3D"
    playlists: str = "EgIQAw%3D%3D"
    livestreams: str = "EgJAAQ%3D%3D"


class VideoUploadDateFilter:
    lastHour: str = "EgQIARAB"
    today: str = "EgQIAhAB"
    thisWeek: str = "EgQIAxAB"
    thisMonth: str = "EgQIBBAB"
    thisYear: str = "EgQIBRAB"


class VideoDurationFilter:
    short: str = "EgQQARgB"
    long: str = "EgQQARgC"


class VideoSortOrder:
    relevance: str = "CAASAhAB"
    uploadDate: str = "CAISAhAB"
    viewCount: str = "CAMSAhAB"
    rating: str = "CAESAhAB"


class ChannelRequestType:
    info: str = "EgVhYm91dA%3D%3D"
    playlists: str = "EglwbGF5bGlzdHPyBgQKAkIA"
