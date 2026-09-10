import asyncio
import copy
import inspect
import json
import logging
import os
from typing import Any, Callable, Dict, Mapping, Optional, Tuple
from urllib.parse import urlencode
import aiohttp

from py_yt.core.constants import CLIENT_PROFILES, requestPayload, searchKey, userAgent
from py_yt.core.session import (
    get_session,
    get_session_po_token,
    get_session_po_token_verifier,
    get_session_visitor_data,
    get_token_lock,
    set_session_po_token,
    set_session_visitor_data,
)

logger = logging.getLogger(__name__)

CLIENT_PROFILE_KEYS = ["WEB", "MWEB", "ANDROID_VR", "TVHTML5"]


class RequestCore:
    def __init__(
        self,
        timeout: float = 7.0,
        max_retries: int = 2,
        proxy: Optional[str] = None,
        visitor_data: Optional[str] = None,
        po_token: Optional[str] = None,
        po_token_verifier: Optional[Callable[..., Any]] = None,
    ) -> None:
        self.url: Optional[str] = None
        self.data: Optional[Dict[str, Any]] = None
        self.timeout: float = timeout
        self.max_retries: int = max_retries
        self.proxy_url: Optional[str] = proxy or os.environ.get("PROXY_URL")
        self.visitor_data: Optional[str] = visitor_data
        self.po_token: Optional[str] = po_token
        self.po_token_verifier: Optional[Callable[..., Any]] = po_token_verifier

    @staticmethod
    def _build_url(endpoint: str, extra_params: Optional[Dict[str, str]] = None) -> str:
        """Helper to construct YouTube InnerTube endpoint URLs."""
        params: Dict[str, str] = {"key": searchKey}
        if extra_params:
            params.update(extra_params)
        return f"https://www.youtube.com/youtubei/v1/{endpoint}?{urlencode(params)}"

    @staticmethod
    def _build_payload(
        language: str = "en",
        region: str = "US",
        client_name: str = "WEB",
        client_version: str = "2.20260820.08.00",
        continuation: Optional[str] = None,
        params: Optional[str] = None,
        **extra_fields: Any,
    ) -> Dict[str, Any]:
        """Helper to build standardized InnerTube request payloads."""
        payload: Dict[str, Any] = copy.deepcopy(requestPayload)
        client_dict = payload["context"]["client"]
        client_dict["hl"] = language
        client_dict["gl"] = region
        client_dict["clientName"] = client_name
        client_dict["clientVersion"] = client_version

        if params:
            payload["params"] = params
        if continuation:
            payload["continuation"] = continuation

        for key, val in extra_fields.items():
            if val is not None:
                payload[key] = val

        return payload

    async def _fetch_automatic_visitor_data(self) -> Optional[str]:
        try:
            session = await get_session()
            url = self._build_url("visitor_id")
            payload = {
                "context": {
                    "client": {
                        "hl": "en",
                        "gl": "US",
                        "clientName": "WEB",
                        "clientVersion": "2.20260820.08.00",
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

    async def _resolve_tokens(self) -> Tuple[Optional[str], Optional[str]]:
        visitor_data = self.visitor_data or get_session_visitor_data()
        po_token = self.po_token or get_session_po_token()
        verifier = self.po_token_verifier or get_session_po_token_verifier()

        if visitor_data and po_token and not verifier:
            self.visitor_data = visitor_data
            self.po_token = po_token
            return visitor_data, po_token

        async with get_token_lock():
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
                        visitor_data = (
                            res.get("visitor_data")
                            or res.get("visitorData")
                            or visitor_data
                        )
                    elif isinstance(res, str):
                        po_token = res
                except Exception as e:
                    logger.warning(f"Error calling po_token_verifier: {e}")

            if not po_token:
                try:
                    from py_yt.botGuard.bot_guard import generate_po_token

                    video_id = getattr(self, "video_id", None) or "dQw4w9WgXcQ"
                    gen_pot = await asyncio.to_thread(
                        generate_po_token, video_id=video_id
                    )
                    if gen_pot and isinstance(gen_pot, str):
                        po_token = gen_pot
                except Exception as e:
                    logger.debug(f"botGuard token generation failed: {e}")

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

    def _prepare_request_for_profile(self, profile_name: str) -> Dict[str, str]:
        profile = CLIENT_PROFILES.get(profile_name, CLIENT_PROFILES["WEB"])
        headers: Dict[str, str] = {
            "User-Agent": profile.get("userAgent", userAgent),
            "Origin": "https://www.youtube.com",
            "Referer": "https://www.youtube.com/",
            "Accept-Language": "en-US,en;q=0.9",
            "X-YouTube-Client-Name": profile.get("clientCode", "1"),
            "X-YouTube-Client-Version": profile.get(
                "clientVersion", "2.20260820.08.00"
            ),
        }

        if self.visitor_data:
            headers["X-Goog-Visitor-Id"] = self.visitor_data
        else:
            headers.pop("X-Goog-Visitor-Id", None)

        if isinstance(self.data, dict):
            context = self.data.setdefault("context", {})
            client = context.setdefault("client", {})
            client["clientName"] = profile["clientName"]
            client["clientVersion"] = profile["clientVersion"]
            if self.visitor_data:
                client["visitorData"] = self.visitor_data
            else:
                client.pop("visitorData", None)
            if self.po_token:
                client["serviceIntegrityDimensions"] = {"poToken": self.po_token}
            else:
                client.pop("serviceIntegrityDimensions", None)

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

    def _get_headers(self) -> Dict[str, str]:
        if isinstance(self.data, dict):
            client_name = (
                self.data.get("context", {}).get("client", {}).get("clientName", "WEB")
            )
            return self._prepare_request_for_profile(client_name)
        return self._prepare_request_for_profile("WEB")

    def _extract_visitor_data_from_response(
        self,
        response_bytes: bytes,
        response_headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        try:
            if response_headers and "X-Goog-Visitor-Id" in response_headers:
                vd_hdr = response_headers["X-Goog-Visitor-Id"]
                if vd_hdr:
                    self.visitor_data = vd_hdr
                    set_session_visitor_data(vd_hdr)
                    return
            data = json.loads(response_bytes.decode("utf-8", errors="ignore"))
            vd: Optional[str] = None
            if isinstance(data, dict):
                extracted_vd = (
                    data.get("responseContext", {}).get("visitorData")
                    or data.get("responseHeader", {}).get("visitorData")
                    or data.get("visitorData")
                )
                if isinstance(extracted_vd, str):
                    vd = extracted_vd
            if vd:
                self.visitor_data = vd
                set_session_visitor_data(vd)
        except Exception:
            pass

    async def post_request(self,client_profiles: Optional[list[str]] = None, exc_info: bool = True) -> Optional[aiohttp.ClientResponse]:
        """Sends an asynchronous POST request."""
        if not self.url:
            raise ValueError("URL must be set before making a request.")

        await self._resolve_tokens()
        session = await get_session()
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        profiles = client_profiles or CLIENT_PROFILE_KEYS

        for i in range(self.max_retries + 1):
            profile_name = profiles[i % len(profiles)]
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
                    if response is not None:
                        response.release()
                    raise
            except aiohttp.ClientResponseError as e:
                is_last_retry = i == self.max_retries
                log_fn = logger.error if is_last_retry else logger.debug
                log_fn(
                    f"HTTP error during POST request (attempt {i + 1}/{self.max_retries + 1}, profile={profile_name})",
                    extra={
                        "status_code": e.status,
                        "response_text": e.message,
                        "url": self.url,
                    },
                    exc_info=is_last_retry and exc_info,
                )
            except (aiohttp.ClientError, asyncio.TimeoutError):
                is_last_retry = i == self.max_retries
                log_fn = logger.error if is_last_retry else logger.debug
                log_fn(
                    f"Request error during POST request (attempt {i + 1}/{self.max_retries + 1}, profile={profile_name})",
                    extra={
                        "request_url": self.url,
                    },
                    exc_info=is_last_retry and exc_info,
                )
            if i < self.max_retries:
                await asyncio.sleep(2**i)
        return None

    async def get_request(self) -> Optional[aiohttp.ClientResponse]:
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
            response = None

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
                    if response is not None:
                        response.release()
                    raise
            except aiohttp.ClientResponseError as e:
                is_last_retry = i == self.max_retries
                log_fn = logger.error if is_last_retry else logger.debug
                log_fn(
                    f"HTTP error during GET request (attempt {i + 1}/{self.max_retries + 1}, profile={profile_name})",
                    extra={
                        "status_code": e.status,
                        "response_text": e.message,
                        "url": self.url,
                    },
                    exc_info=is_last_retry,
                )
            except (aiohttp.ClientError, asyncio.TimeoutError):
                is_last_retry = i == self.max_retries
                log_fn = logger.error if is_last_retry else logger.debug
                log_fn(
                    f"Request error during GET request (attempt {i + 1}/{self.max_retries + 1}, profile={profile_name})",
                    extra={
                        "request_url": self.url,
                    },
                    exc_info=is_last_retry,
                )
            if i < self.max_retries:
                await asyncio.sleep(2**i)
        return None
