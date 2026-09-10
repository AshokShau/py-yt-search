import asyncio
from typing import Optional
import aiohttp

_session: Optional[aiohttp.ClientSession] = None
_token_lock: Optional[asyncio.Lock] = None


def get_token_lock() -> asyncio.Lock:
    """Returns an asyncio.Lock for synchronized token resolution."""
    global _token_lock
    current_loop = asyncio.get_running_loop()
    if _token_lock is None or getattr(_token_lock, "_loop", None) != current_loop:
        _token_lock = asyncio.Lock()
    return _token_lock


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
