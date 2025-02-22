# YouTube Data Extraction with PY-YT

This project demonstrates how to use the `py-yt` library to interact with YouTube's data, including searching for videos, channels, playlists, retrieving video details, extracting comments, transcripts, and fetching search suggestions.

## Features
- Search YouTube for videos, channels, and playlists
- Retrieve video information and available formats
- Extract comments from videos
- Get video transcripts in different languages
- Fetch search suggestions from YouTube
- Retrieve details of YouTube channels and their playlists

## Installation
Make sure you have Python installed (>=3.8). Install `py-yt` using:

```bash
pip install git+https://github.com/AshokShau/py-yt@master
```

```bash
pip install py-yt-search
```

## Usage
The script uses `asyncio` to execute YouTube queries asynchronously. Below is an overview of the main functions:

### Search YouTube
```python
_search = Search('NoCopyrightSounds', limit=1, language='en', region='US')
result = await _search.next()
print(result)
```

### Search for Videos Only
```python
videosSearch = VideosSearch('NoCopyrightSounds', limit=10, language='en', region='US')
videosResult = await videosSearch.next()
print(videosResult)
```

### Search for Channels Only
```python
channelsSearch = ChannelsSearch('NoCopyrightSounds', limit=1, language='en', region='US')
channelsResult = await channelsSearch.next()
print(channelsResult)
```

### Search for Playlists Only
```python
playlistsSearch = PlaylistsSearch('NoCopyrightSounds', limit=1, language='en', region='US')
playlistsResult = await playlistsSearch.next()
print(playlistsResult)
```

### Get Video Details
```python
video = await Video.get('z0GKGpObgPY')
print(video)
```

### Get Playlist Details
```python
playlist = await Playlist.get('https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK')
print(playlist)
```

### Fetch Comments from a Video
```python
comments = Comments('_ZdsmLgCVdU')
await comments.getNextComments()
print(len(comments.comments['result']))
```

### Retrieve Video Transcript
```python
transcript = await Transcript.get('https://www.youtube.com/watch?v=L7kF4MXXCoA')
print(transcript)
```

### Get YouTube Search Suggestions
```python
suggestions = await Suggestions.get('NoCopyrightSounds', language='en', region='US')
print(suggestions)
```

## Running the Script
To run the script, execute:
```bash
python script.py
```

Ensure `asyncio.run(main())` is at the end of the script to handle async execution.

## Notes
- The script uses `asyncio` for efficient asynchronous operations.
- Some operations may require multiple calls to retrieve all available data (e.g., pagination for comments and playlists).
- `yt-py` provides various search filters to refine results, such as sorting by upload date or filtering by duration.

## License
This project is licensed under the MIT License. See the [LICENSE](/LICENSE) file for details.

## Credits
This project is based on [youtube-search-python](https://github.com/alexmercerind/youtube-search-python) by Alex Mercer.
