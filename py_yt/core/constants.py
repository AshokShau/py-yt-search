requestPayload = {
    "context": {
        "client": {
            "hl": "en",
            "gl": "US",
            "clientName": "WEB",
            "clientVersion": "2.20251021.01.00",
            "newVisitorCookie": True,
        },
        "user": {
            "lockedSafetyMode": False,
        },
    }
}

userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

CLIENT_PROFILES = {
    "WEB": {
        "clientName": "WEB",
        "clientVersion": "2.20251021.01.00",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "clientCode": "1",
    },
    "ANDROID_VR": {
        "clientName": "ANDROID_VR",
        "clientVersion": "1.61.26",
        "userAgent": "Mozilla/5.0 (Linux; Android 12; Quest 3) AppleWebKit/537.36 (KHTML, like Gecko) OculusBrowser/32.0.0.3.17 Chrome/122.0.6261.64 Mobile Safari/537.36",
        "clientCode": "93",
    },
    "MWEB": {
        "clientName": "MWEB",
        "clientVersion": "2.20251021.01.00",
        "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
        "clientCode": "2",
    },
    "TVHTML5": {
        "clientName": "TVHTML5",
        "clientVersion": "7.20251021.00.00",
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

videoElementKey = "videoRenderer"
channelElementKey = "channelRenderer"
playlistElementKey = "playlistRenderer"
shelfElementKey = "shelfRenderer"
itemSectionKey = "itemSectionRenderer"
continuationItemKey = "continuationItemRenderer"
playerResponseKey = "playerResponse"
richItemKey = "richItemRenderer"
hashtagElementKey = "hashtagTileRenderer"
hashtagBrowseKey = "FEhashtag"
hashtagVideosPath = [
    "contents",
    "twoColumnBrowseResultsRenderer",
    "tabs",
    0,
    "tabRenderer",
    "content",
    "richGridRenderer",
    "contents",
]
hashtagContinuationVideosPath = [
    "onResponseReceivedActions",
    0,
    "appendContinuationItemsAction",
    "continuationItems",
]
searchKey = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
contentPath = [
    "contents",
    "twoColumnSearchResultsRenderer",
    "primaryContents",
    "sectionListRenderer",
    "contents",
]
fallbackContentPath = [
    "contents",
    "twoColumnSearchResultsRenderer",
    "primaryContents",
    "richGridRenderer",
    "contents",
]
continuationContentPath = [
    "onResponseReceivedCommands",
    0,
    "appendContinuationItemsAction",
    "continuationItems",
]
continuationKeyPath = [
    "continuationItemRenderer",
    "continuationEndpoint",
    "continuationCommand",
    "token",
]
playlistInfoPath = ["response", "sidebar", "playlistSidebarRenderer", "items"]
playlistVideosPath = [
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
playlistPrimaryInfoKey = "playlistSidebarPrimaryInfoRenderer"
playlistSecondaryInfoKey = "playlistSidebarSecondaryInfoRenderer"
playlistVideoKey = "playlistVideoRenderer"


class ResultMode:
    json = 0
    dict = 1


class SearchMode:
    videos = "EgIQAQ%3D%3D"
    channels = "EgIQAg%3D%3D"
    playlists = "EgIQAw%3D%3D"
    livestreams = "EgJAAQ%3D%3D"


class VideoUploadDateFilter:
    lastHour = "EgQIARAB"
    today = "EgQIAhAB"
    thisWeek = "EgQIAxAB"
    thisMonth = "EgQIBBAB"
    thisYear = "EgQIBRAB"


class VideoDurationFilter:
    short = "EgQQARgB"
    long = "EgQQARgC"


class VideoSortOrder:
    relevance = "CAASAhAB"
    uploadDate = "CAISAhAB"
    viewCount = "CAMSAhAB"
    rating = "CAESAhAB"


class ChannelRequestType:
    info = "EgVhYm91dA%3D%3D"
    playlists = "EglwbGF5bGlzdHMYAyABcAA%3D"
