import os
import logging

import httpx
from py_yt.core.constants import userAgent

logger = logging.getLogger(__name__)


class RequestCore:
    def __init__(self, timeout: float = 7.0, max_retries: int = 0):
        self.url: str | None = None
        self.data: dict | None = None
        self.timeout: float = timeout
        self.max_retries: int = max_retries
        self.proxy_url: str | None = os.environ.get("PROXY_URL")
        client_args = {"timeout": self.timeout, "proxy": self.proxy_url}

        self.async_client = httpx.AsyncClient(**client_args)

    async def asyncPostRequest(self) -> httpx.Response | None:
        """Sends an asynchronous POST request."""
        if not self.url:
            raise ValueError("URL must be set before making a request.")

        headers = {"User-Agent": userAgent}

        for _ in range(self.max_retries + 1):
            try:
                response = await self.async_client.post(
                    self.url,
                    headers=headers,
                    json=self.data,
                )
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                logger.error(
                    "HTTP error during HTTP request",
                    extra={
                        "status_code": getattr(e.response, "status_code", None),
                        "response_text": getattr(e.response, "text", None),
                    },
                    exc_info=True,
                )
            except httpx.RequestError as e:
                logger.error(
                    "Request error during HTTP request",
                    extra={
                        "request_url": getattr(getattr(e, "request", None), "url", None),
                    },
                    exc_info=True,
                )
        return None

    async def asyncGetRequest(self) -> httpx.Response | None:
        """Sends an asynchronous GET request."""
        if not self.url:
            raise ValueError("URL must be set before making a request.")
        cookies = {"CONSENT": "YES+1"}
        for _ in range(self.max_retries + 1):
            try:
                response = await self.async_client.get(
                    self.url,
                    headers={"User-Agent": userAgent},
                    cookies=cookies,
                )
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                logger.error(
                    "HTTP error during HTTP request",
                    extra={
                        "status_code": getattr(e.response, "status_code", None),
                        "response_text": getattr(e.response, "text", None),
                    },
                    exc_info=True,
                )
            except httpx.RequestError as e:
                logger.error(
                    "Request error during HTTP request",
                    extra={
                        "request_url": getattr(getattr(e, "request", None), "url", None),
                    },
                    exc_info=True,
                )
        return None
