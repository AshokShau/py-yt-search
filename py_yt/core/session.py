import asyncio
from typing import Any, Callable, Optional, Union
import aiohttp

_session: Optional[aiohttp.ClientSession] = None
_visitor_data: Optional[str] = None
_po_token: Optional[str] = None
_po_token_verifier: Optional[Callable[..., Any]] = None
_token_lock: Optional[asyncio.Lock] = None


def get_token_lock() -> asyncio.Lock:
    """Returns an asyncio.Lock for synchronized token resolution."""
    global _token_lock
    current_loop = asyncio.get_running_loop()
    if _token_lock is None or getattr(_token_lock, "_loop", None) != current_loop:
        _token_lock = asyncio.Lock()
    return _token_lock


def set_session_visitor_data(visitor_data: Optional[str]) -> None:
    """Sets the persistent visitorData for session requests."""
    global _visitor_data
    _visitor_data = visitor_data


def get_session_visitor_data() -> Optional[str]:
    """Gets the persistent visitorData."""
    global _visitor_data
    return _visitor_data


def set_session_po_token(po_token: Optional[str]) -> None:
    """Sets the persistent poToken for session requests."""
    global _po_token
    _po_token = po_token


def get_session_po_token() -> Optional[str]:
    """Gets the persistent poToken."""
    global _po_token
    return _po_token


def set_session_po_token_verifier(verifier: Optional[Callable[..., Any]]) -> None:
    """Sets a global callable or function to retrieve poToken / visitorData dynamically."""
    global _po_token_verifier
    _po_token_verifier = verifier


def get_session_po_token_verifier() -> Optional[Callable[..., Any]]:
    """Gets the registered po_token_verifier."""
    global _po_token_verifier
    return _po_token_verifier


async def get_session() -> aiohttp.ClientSession:
    """Returns a shared aiohttp.ClientSession, creating it if it doesn't exist."""
    global _session
    current_loop = asyncio.get_running_loop()
    if (
        _session is None
        or _session.closed
        or _session._loop != current_loop
        or _session._loop.is_closed()
    ):
        _session = aiohttp.ClientSession()
    return _session


async def close_session() -> None:
    """Closes the shared aiohttp.ClientSession."""
    global _session
    if _session is not None and not _session.closed:
        await _session.close()
        _session = None
