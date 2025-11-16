import os
import aiohttp
from aiohttp import ClientTimeout
from py_yt.core.constants import userAgent


class RequestCore:
    def __init__(self, timeout: int = 5):
        self.url = None
        self.data = None
        self.timeout = timeout
        self.proxy_url = os.environ.get("PROXY_URL")
        self.async_session = None

    async def asyncPostRequest(self) -> aiohttp.ClientResponse | None:
        """Sends an asynchronous POST request."""
        if not self.url:
            raise ValueError("URL must be set before making a request.")
        if self.async_session is None:
            raise RuntimeError(
                "async_session is not initialized. Use 'async with' context manager."
            )
        try:
            response = await self.async_session.post(
                self.url,
                headers={"User-Agent": userAgent},
                json=self.data,
                proxy=self.proxy_url,
            )
            response.raise_for_status()
            return response
        except aiohttp.ClientResponseError as e:
            print(f"HTTP error: {e.status} - {e.message}")
            return None
        except aiohttp.ClientError as e:
            print(f"Request error: {e}")
            return None

    async def asyncGetRequest(self) -> aiohttp.ClientResponse | None:
        """Sends an asynchronous GET request."""
        if not self.url:
            raise ValueError("URL must be set before making a request.")
        if self.async_session is None:
            raise RuntimeError(
                "async_session is not initialized. Use 'async with' context manager."
            )
        cookies = {"CONSENT": "YES+1"}
        try:
            response = await self.async_session.get(
                self.url,
                headers={"User-Agent": userAgent},
                cookies=cookies,
                proxy=self.proxy_url,
            )
            response.raise_for_status()
            return response
        except aiohttp.ClientResponseError as e:
            print(f"HTTP error: {e.status} - {e.message}")
            return None
        except aiohttp.ClientError as e:
            print(f"Request error: {e}")
            return None

    async def __aenter__(self):
        self.async_session = aiohttp.ClientSession(
            timeout=ClientTimeout(total=self.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.async_session:
            await self.async_session.close()
