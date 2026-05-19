import aiohttp
import asyncio

_session = None

async def get_session() -> aiohttp.ClientSession:
    """Returns a shared aiohttp.ClientSession, creating it if it doesn't exist."""
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession()
    return _session

async def close_session():
    """Closes the shared aiohttp.ClientSession."""
    global _session
    if _session is not None and not _session.closed:
        await _session.close()
        _session = None
