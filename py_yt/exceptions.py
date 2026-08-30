class PyYTSearchError(Exception):
    """Base exception for all py-yt-search errors."""

    pass


class ParsingError(PyYTSearchError):
    """Raised when parsing YouTube API or HTML responses fails."""

    pass


class RequestError(PyYTSearchError):
    """Raised when HTTP request to YouTube fails or returns invalid response."""

    pass


class VideoNotFoundError(PyYTSearchError):
    """Raised when a video is not found or inaccessible."""

    pass
