import aiohttp
import asyncio

_session = None
_visitor_data: str | None = None
_po_token: str | None = None
_po_token_verifier = None

def set_session_visitor_data(visitor_data: str | None) -> None:
    """Sets the persistent visitorData for session requests."""
    global _visitor_data
    _visitor_data = visitor_data

def get_session_visitor_data() -> str | None:
    """Gets the persistent visitorData."""
    global _visitor_data
    return _visitor_data

def set_session_po_token(po_token: str | None) -> None:
    """Sets the persistent poToken for session requests."""
    global _po_token
    _po_token = po_token

def get_session_po_token() -> str | None:
    """Gets the persistent poToken."""
    global _po_token
    return _po_token

def set_session_po_token_verifier(verifier) -> None:
    """Sets a global callable or function to retrieve poToken / visitorData dynamically."""
    global _po_token_verifier
    _po_token_verifier = verifier

def get_session_po_token_verifier():
    """Gets the registered po_token_verifier."""
    global _po_token_verifier
    return _po_token_verifier

async def get_session() -> aiohttp.ClientSession:
    """Returns a shared aiohttp.ClientSession, creating it if it doesn't exist."""
    global _session
    current_loop = asyncio.get_running_loop()
    if _session is None or _session.closed or _session._loop != current_loop or _session._loop.is_closed():
        _session = aiohttp.ClientSession()
    return _session

async def close_session():
    """Closes the shared aiohttp.ClientSession."""
    global _session
    if _session is not None and not _session.closed:
        await _session.close()
        _session = None
