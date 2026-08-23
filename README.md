# YouTube Data Extraction with py-yt-search

`py-yt-search` is an async-first Python library for searching and retrieving YouTube data, including videos, channels, playlists, transcripts, search suggestions, recommendations, and **HYPE HINT** momentum analytics.

## Features
- **Async-first architecture**: built for high-performance `asyncio` applications.
- **YouTube Search**: search for videos, channels, playlists, or perform filtered search.
- **Channel Search**: search for videos within a specific YouTube channel.
- **HYPE HINT**: calculate momentum, view velocity, recency boost, and rank videos by hype scores.
- **Video & Format Details**: retrieve detailed video metadata, formats, and streaming data.
- **Playlist Details**: fetch full playlist info and paginate through playlist videos (supports standard & YouTube Mix playlists).
- **Video Transcripts**: extract video subtitles/transcripts across supported languages.
- **Suggestions & Recommendations**: fetch live search suggestions and homepage/related video recommendations.
- **Resilient Network Layer**: automatic client profile rotation, visitor token persistence, and retry backoff.

## Installation

```bash
pip install py-yt-search
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/AshokShau/py-yt-search.git
```

## Usage

All API calls in `py-yt-search` are asynchronous and should be executed within an `asyncio` event loop.

### 1. Search YouTube

```python
import asyncio
from py_yt import Search, VideosSearch, ChannelsSearch, PlaylistsSearch

async def main():
    # General Search (videos, channels, playlists)
    search = Search('Python programming', limit=5)
    result = await search.next()
    print("Search results count:", len(result['result']))

    # Video Search Only
    videos_search = VideosSearch('Python tutorial', limit=5)
    videos_result = await videos_search.next()
    print("First video title:", videos_result['result'][0]['title'])

    # Channels Search
    channels_search = ChannelsSearch('Python Software Foundation', limit=1)
    channels_result = await channels_search.next()
    print("Channel ID:", channels_result['result'][0]['id'])

    # Playlists Search
    playlists_search = PlaylistsSearch('Python Data Science', limit=2)
    playlists_result = await playlists_search.next()
    print("Playlist ID:", playlists_result['result'][0]['id'])

asyncio.run(main())
```

### 2. HYPE HINT Momentum Analytics

Calculate video hype scores (0.0 - 100.0) based on view velocity, publication age, log view scaling, and recency boost.

```python
import asyncio
from py_yt import VideosSearch, HypeHint

async def main():
    search = VideosSearch('artificial intelligence', limit=10)
    res = await search.next()
    videos = res.get('result', [])

    # Calculate hype score for a single video
    for video in videos:
        analysis = HypeHint.analyze_video(video)
        print(f"Title: {video['title']}")
        print(f"Hype Score: {analysis['score']}/100 ({analysis['level']})")
        print(f"View Velocity: {analysis['velocity_views_per_hour']} views/hr\n")

    # Rank a list of videos by hype score descending
    ranked_videos = HypeHint.rank(videos)
    print("Top Hyped Video:", ranked_videos[0]['title'])

asyncio.run(main())
```

### 3. Get Video Details

```python
import asyncio
from py_yt import Video

async def main():
    # Get video info
    video_data = await Video.get('z0GKGpObgPY')
    print(video_data)

    # Get streaming formats
    formats = await Video.getFormats('z0GKGpObgPY')
    print(formats)

asyncio.run(main())
```

### 4. Get Playlist Details

```python
import asyncio
from py_yt import Playlist

async def main():
    playlist_url = 'https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK'
    playlist = Playlist(playlist_url)
    
    # Paginate through playlist videos
    await playlist.getNextVideos()
    print(f"Fetched {len(playlist.videos)} videos.")
    print("Has more videos:", playlist.hasMoreVideos)

asyncio.run(main())
```

### 5. Fetch Search Suggestions

```python
import asyncio
from py_yt import Suggestions

async def main():
    suggestions = await Suggestions.get('python', language='en', region='US')
    print(suggestions['result'])

asyncio.run(main())
```

### 6. Retrieve Video Transcripts

```python
import asyncio
from py_yt import Transcript

async def main():
    transcript = await Transcript.get('https://www.youtube.com/watch?v=L7kF4MXXCoA')
    print(transcript)

asyncio.run(main())
```

### 7. Recommendations & Related Videos

```python
import asyncio
from py_yt import Recommendations

async def main():
    # Get homepage recommendations
    home = await Recommendations.getHome(limit=5)
    print("Home videos:", len(home['result']))

    # Get related / suggested videos for a watch URL
    related = await Recommendations.getRelated('https://www.youtube.com/watch?v=z0GKGpObgPY', limit=5)
    print("Related videos:", len(related['result']))

asyncio.run(main())
```

## Error Handling

`py-yt-search` defines custom exception types under `py_yt.exceptions`:

- `PyYTSearchError`: base exception class.
- `ParsingError`: raised when parsing YouTube API or HTML structure fails.
- `RequestError`: raised when HTTP network requests fail.
- `VideoNotFoundError`: raised when video details are missing or inaccessible.

```python
from py_yt import VideosSearch
from py_yt.exceptions import PyYTSearchError

async def safe_search():
    try:
        search = VideosSearch('python', limit=5)
        res = await search.next()
        print(res)
    except PyYTSearchError as e:
        print(f"py-yt-search error occurred: {e}")
```

## License
This project is licensed under the MIT License. See the [LICENSE](/LICENSE) file for details.

## Credits
This project is based on [youtube-search-python](https://github.com/alexmercerind/youtube-search-python) by Alex Mercer.
