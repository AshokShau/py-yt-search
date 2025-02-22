import httpx
from py_yt.core.constants import userAgent


class RequestCore:
    def __init__(self, timeout: float = 3.0):
        self.url: str | None = None
        self.data: dict | None = None
        self.timeout: float = timeout
        self.async_client = httpx.AsyncClient(timeout=self.timeout)

    async def asyncPostRequest(self) -> httpx.Response | None:
        """Sends an asynchronous POST request."""
        if not self.url:
            raise ValueError("URL must be set before making a request.")
        try:
            response = await self.async_client.post(
                self.url,
                headers={"User-Agent": userAgent},
                json=self.data,
            )
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"Request error: {e}")
        return None

    async def asyncGetRequest(self) -> httpx.Response | None:
        """Sends an asynchronous GET request."""
        if not self.url:
            raise ValueError("URL must be set before making a request.")
        cookies = {'CONSENT': 'YES+1'}
        try:
            response = await self.async_client.get(
                self.url,
                headers={"User-Agent": userAgent},
                cookies=cookies,
            )
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"Request error: {e}")
        return None
