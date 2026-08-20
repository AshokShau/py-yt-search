import os
import logging
import json
import asyncio
import inspect
from urllib.parse import urlencode
import aiohttp

from py_yt.core.constants import userAgent, CLIENT_PROFILES, searchKey
from py_yt.core.session import (
    get_session,
    get_session_visitor_data,
    set_session_visitor_data,
    get_session_po_token,
    set_session_po_token,
    get_session_po_token_verifier,
)

logger = logging.getLogger(__name__)

CLIENT_PROFILE_KEYS = ["WEB", "MWEB"]


class RequestCore:
    def __init__(
        self,
        timeout: float = 7.0,
        max_retries: int = 2,
        proxy: str | None = None,
        visitor_data: str | None = None,
        po_token: str | None = None,
        po_token_verifier=None,
    ):
        self.url: str | None = None
        self.data: dict | None = None
        self.timeout: float = timeout
        self.max_retries: int = max_retries
        self.proxy_url: str | None = proxy or os.environ.get("PROXY_URL")
        self.visitor_data: str | None = visitor_data
        self.po_token: str | None = po_token
        self.po_token_verifier = po_token_verifier

    async def _fetch_automatic_visitor_data(self) -> str | None:
        try:
            session = await get_session()
            url = (
                "https://www.youtube.com/youtubei/v1/visitor_id"
                + "?"
                + urlencode({"key": searchKey})
            )
            payload = {
                "context": {
                    "client": {
                        "hl": "en",
                        "gl": "US",
                        "clientName": "WEB",
                        "clientVersion": "2.20251021.01.00",
                    }
                }
            }
            timeout = aiohttp.ClientTimeout(total=3.0)
            async with session.post(
                url, json=payload, proxy=self.proxy_url, timeout=timeout
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    vd = data.get("responseContext", {}).get("visitorData")
                    if vd and isinstance(vd, str):
                        return vd
        except Exception as e:
            logger.debug(f"Automatic visitor_id fetch failed: {e}")
        return None

    async def _fetch_from_pot_provider(self) -> tuple[str | None, str | None]:
        pot_url = os.environ.get("POT_PROVIDER_URL")
        if not pot_url:
            return None, None
        try:
            session = await get_session()
            timeout = aiohttp.ClientTimeout(total=2.0)
            async with session.post(pot_url, json={}, proxy=self.proxy_url, timeout=timeout) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    po_token = data.get("poToken") or data.get("po_token")
                    visitor_data = data.get("visitorData") or data.get("visitor_data")
                    return visitor_data, po_token
        except Exception:
            pass
        return None, None

    async def _resolve_tokens(self) -> tuple[str | None, str | None]:
        visitor_data = self.visitor_data or get_session_visitor_data()
        po_token = self.po_token or get_session_po_token()
        verifier = self.po_token_verifier or get_session_po_token_verifier()

        if verifier and callable(verifier):
            try:
                if inspect.iscoroutinefunction(verifier):
                    res = await verifier()
                else:
                    res = verifier()

                if isinstance(res, tuple) and len(res) == 2:
                    a, b = res
                    if isinstance(a, str) and isinstance(b, str):
                        if "Cg" in a or "%3D" in a or len(a) > len(b):
                            visitor_data, po_token = a, b
                        else:
                            po_token, visitor_data = a, b
                elif isinstance(res, dict):
                    po_token = res.get("po_token") or res.get("poToken") or po_token
                    visitor_data = res.get("visitor_data") or res.get("visitorData") or visitor_data
                elif isinstance(res, str):
                    po_token = res
            except Exception as e:
                logger.warning(f"Error calling po_token_verifier: {e}")

        if not po_token or not visitor_data:
            prov_vd, prov_po = await self._fetch_from_pot_provider()
            visitor_data = visitor_data or prov_vd
            po_token = po_token or prov_po

        if not po_token:
            try:
                from py_yt.botGuard.bot_guard import generate_po_token
                video_id = getattr(self, "video_id", None) or "dQw4w9WgXcQ"
                gen_pot = generate_po_token(video_id=video_id)
                if gen_pot and isinstance(gen_pot, str):
                    po_token = gen_pot
            except Exception:
                pass

        if not visitor_data:
            auto_vd = await self._fetch_automatic_visitor_data()
            if auto_vd:
                visitor_data = auto_vd

        self.visitor_data = visitor_data
        self.po_token = po_token
        if visitor_data:
            set_session_visitor_data(visitor_data)
        if po_token:
            set_session_po_token(po_token)
        return visitor_data, po_token

    def _prepare_request_for_profile(self, profile_name: str) -> dict[str, str]:
        profile = CLIENT_PROFILES.get(profile_name, CLIENT_PROFILES["WEB"])
        headers = {
            "User-Agent": profile.get("userAgent", userAgent),
            "Origin": "https://www.youtube.com",
            "Referer": "https://www.youtube.com/",
            "Accept-Language": "en-US,en;q=0.9",
            "X-YouTube-Client-Name": profile.get("clientCode", "1"),
            "X-YouTube-Client-Version": profile.get("clientVersion", "2.20251021.01.00"),
        }

        if self.visitor_data:
            headers["X-Goog-Visitor-Id"] = self.visitor_data

        if isinstance(self.data, dict):
            context = self.data.setdefault("context", {})
            client = context.setdefault("client", {})
            client["clientName"] = profile["clientName"]
            client["clientVersion"] = profile["clientVersion"]
            if self.visitor_data:
                client["visitorData"] = self.visitor_data
            if self.po_token:
                client["serviceIntegrityDimensions"] = {"poToken": self.po_token}

            client_name = client.get("clientName")
            client_version = client.get("clientVersion")
            client_name_map = {
                "WEB": "1",
                "MWEB": "2",
                "ANDROID": "3",
                "IOS": "5",
                "TVHTML5": "7",
                "ANDROID_TESTSUITE": "82",
                "ANDROID_VR": "93",
            }
            if client_name in client_name_map:
                headers["X-YouTube-Client-Name"] = client_name_map[client_name]
            if client_version:
                headers["X-YouTube-Client-Version"] = str(client_version)

        return headers

    def _get_headers(self) -> dict[str, str]:
        if isinstance(self.data, dict):
            client_name = self.data.get("context", {}).get("client", {}).get("clientName", "WEB")
            return self._prepare_request_for_profile(client_name)
        return self._prepare_request_for_profile("WEB")

    def _extract_visitor_data_from_response(self, response_bytes: bytes, response_headers=None):
        try:
            if response_headers and "X-Goog-Visitor-Id" in response_headers:
                vd = response_headers["X-Goog-Visitor-Id"]
                if vd:
                    self.visitor_data = vd
                    set_session_visitor_data(vd)
                    return
            data = json.loads(response_bytes.decode("utf-8", errors="ignore"))
            vd = None
            if isinstance(data, dict):
                vd = (
                    data.get("responseContext", {}).get("visitorData")
                    or data.get("responseHeader", {}).get("visitorData")
                    or data.get("visitorData")
                )
            if vd and isinstance(vd, str):
                self.visitor_data = vd
                set_session_visitor_data(vd)
        except Exception:
            pass

    async def postRequest(self) -> aiohttp.ClientResponse | None:
        """Sends an asynchronous POST request."""
        if not self.url:
            raise ValueError("URL must be set before making a request.")

        await self._resolve_tokens()
        session = await get_session()
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        for i in range(self.max_retries + 1):
            profile_name = CLIENT_PROFILE_KEYS[i % len(CLIENT_PROFILE_KEYS)]
            headers = self._prepare_request_for_profile(profile_name)

            try:
                response = await session.post(
                    self.url,
                    headers=headers,
                    json=self.data,
                    proxy=self.proxy_url,
                    timeout=timeout,
                )
                try:
                    response.raise_for_status()
                    content = await response.read()
                    self._extract_visitor_data_from_response(content, response.headers)
                    return response
                except Exception:
                    response.release()
                    raise
            except aiohttp.ClientResponseError as e:
                logger.error(
                    f"HTTP error during POST request (attempt {i+1}/{self.max_retries+1}, profile={profile_name})",
                    extra={
                        "status_code": e.status,
                        "response_text": e.message,
                        "url": self.url
                    },
                    exc_info=True,
                )
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.error(
                    f"Request error during POST request (attempt {i+1}/{self.max_retries+1}, profile={profile_name})",
                    extra={
                        "request_url": self.url,
                    },
                    exc_info=True,
                )
            if i < self.max_retries:
                await asyncio.sleep(1 * (2 ** i))
        return None

    async def getRequest(self) -> aiohttp.ClientResponse | None:
        """Sends an asynchronous GET request."""
        if not self.url:
            raise ValueError("URL must be set before making a request.")

        await self._resolve_tokens()
        cookies = {"CONSENT": "YES+1"}
        session = await get_session()
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        for i in range(self.max_retries + 1):
            profile_name = CLIENT_PROFILE_KEYS[i % len(CLIENT_PROFILE_KEYS)]
            headers = self._prepare_request_for_profile(profile_name)

            try:
                response = await session.get(
                    self.url,
                    headers=headers,
                    cookies=cookies,
                    proxy=self.proxy_url,
                    timeout=timeout,
                )
                try:
                    response.raise_for_status()
                    content = await response.read()
                    self._extract_visitor_data_from_response(content, response.headers)
                    return response
                except Exception:
                    response.release()
                    raise
            except aiohttp.ClientResponseError as e:
                logger.error(
                    f"HTTP error during GET request (attempt {i+1}/{self.max_retries+1}, profile={profile_name})",
                    extra={
                        "status_code": e.status,
                        "response_text": e.message,
                        "url": self.url
                    },
                    exc_info=True,
                )
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.error(
                    f"Request error during GET request (attempt {i+1}/{self.max_retries+1}, profile={profile_name})",
                    extra={
                        "request_url": self.url,
                    },
                    exc_info=True,
                )
            if i < self.max_retries:
                await asyncio.sleep(1 * (2 ** i))
        return None
