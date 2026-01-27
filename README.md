# py-yt-search

🔎 Search for YouTube videos, channels & playlists. Get 🎞 video & 📑 playlist info using link. Get search suggestions. WITHOUT YouTube Data API v3.

---

## Features

* 🔎 Search videos, channels, and playlists
* 📄 Get video metadata + available streams
* 📜 Fetch transcripts (subtitles)
* 📂 Playlist info + all videos
* 👤 Channel info + playlists
* 💡 Search suggestions (autocomplete)
* 🏷 Hashtag search
* 🔁 Pagination support
* 🎛 Custom search filters (date, duration, type, etc.)

---

## Installation

Python **>= 3.8** required.

```bash
pip install git+https://github.com/AshokShau/py-yt-search@master
```

Or PyPI:

```bash
pip install py-yt-search
```

---

## Quick Usage

```python
import asyncio

from py_yt import Search, Video


async def main():
    # Search
    result = await Search("lofi music").next()
    print(result["result"][0]["title"])

    # Video details
    video = await Video().get("https://youtu.be/dQw4w9WgXcQ")
    print(video["title"], video["duration"])

asyncio.run(main())
```

---

## Examples

All working examples are in the `examples/` folder:

| Feature        | File                            |
|----------------|---------------------------------|
| Search         | `examples/search.py`            |
| Pagination     | `examples/search_pagination.py` |
| Video details  | `examples/video.py`             |
| Playlist       | `examples/playlist.py`          |
| Channel info   | `examples/channel.py`           |
| Suggestions    | `examples/suggestions.py`       |
| Custom filters | `examples/custom_search.py`     |
| Hashtag search | `examples/hashtag.py`           |
| Transcripts    | `examples/transcript.py`        |
| Channel search | `examples/channel_search.py`    |

Run any example:

```bash
python3 examples/search.py
```

---

## Notes

* Uses **asyncio** (non-blocking & fast)
* No official YouTube API key needed
* Best used for bots, scrapers, and personal tools

---

## License

MIT License — see [LICENSE](LICENSE)

---

## Credits

Based on
👉 [https://github.com/alexmercerind/youtube-search-python](https://github.com/alexmercerind/youtube-search-python)
by Alex Mercer
