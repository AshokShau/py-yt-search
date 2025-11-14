import os
import aiohttp
from py_yt.core.constants import userAgent
from dotenv import load_dotenv

load_dotenv()

class RequestCore:
    def __init__(self, timeout: float = 3.0):
        self.url: str | None = None
        self.data: dict | None = None
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.proxy_url: str | None = os.environ.get("PROXY_URL")
        self.async_session = aiohttp.ClientSession(timeout=self.timeout)

    async def asyncPostRequest(self) -> aiohttp.ClientResponse | None:
        """Sends an asynchronous POST request."""
        if not self.url:
            raise ValueError("URL must be set before making a request.")
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

    async def close(self):
        """Closes the aiohttp client session."""
        await self.async_session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
