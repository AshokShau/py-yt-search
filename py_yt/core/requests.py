import os
import logging
import asyncio
import aiohttp

from py_yt.core.constants import userAgent
from py_yt.core.session import get_session

logger = logging.getLogger(__name__)


class RequestCore:
    def __init__(
        self, timeout: float = 7.0, max_retries: int = 0, proxy: str | None = None
    ):
        self.url: str | None = None
        self.data: dict | None = None
        self.timeout: float = timeout
        self.max_retries: int = max_retries
        self.proxy_url: str | None = proxy or os.environ.get("PROXY_URL")

    async def asyncPostRequest(self) -> aiohttp.ClientResponse | None:
        """Sends an asynchronous POST request."""
        if not self.url:
            raise ValueError("URL must be set before making a request.")

        headers = {"User-Agent": userAgent}
        session = await get_session()
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        for _ in range(self.max_retries + 1):
            try:
                response = await session.post(
                    self.url,
                    headers=headers,
                    json=self.data,
                    proxy=self.proxy_url,
                    timeout=timeout
                )
                try:
                    response.raise_for_status()
                    await response.read()
                    return response
                except Exception:
                    response.release()
                    raise
            except aiohttp.ClientResponseError as e:
                logger.error(
                    "HTTP error during HTTP request",
                    extra={
                        "status_code": e.status,
                        "response_text": e.message,
                    },
                    exc_info=True,
                )
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.error(
                    "Request error during HTTP request",
                    extra={
                        "request_url": self.url,
                    },
                    exc_info=True,
                )
        return None

    async def asyncGetRequest(self) -> aiohttp.ClientResponse | None:
        """Sends an asynchronous GET request."""
        if not self.url:
            raise ValueError("URL must be set before making a request.")
        cookies = {"CONSENT": "YES+1"}
        session = await get_session()
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        for _ in range(self.max_retries + 1):
            try:
                response = await session.get(
                    self.url,
                    headers={"User-Agent": userAgent},
                    cookies=cookies,
                    proxy=self.proxy_url,
                    timeout=timeout
                )
                try:
                    response.raise_for_status()
                    await response.read()
                    return response
                except Exception:
                    response.release()
                    raise
            except aiohttp.ClientResponseError as e:
                logger.error(
                    "HTTP error during HTTP request",
                    extra={
                        "status_code": e.status,
                        "response_text": e.message,
                    },
                    exc_info=True,
                )
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.error(
                    "Request error during HTTP request",
                    extra={
                        "request_url": self.url,
                    },
                    exc_info=True,
                )
        return None
