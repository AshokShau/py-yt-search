import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from py_yt.core.componenthandler import build_channel_url, get_value, get_video_id
from py_yt.core.requests import RequestCore
from py_yt.exceptions import RequestError

logger = logging.getLogger(__name__)


@dataclass
class Comment:
    id: str
    text: str
    author: str
    author_id: Optional[str] = None
    like_count: Optional[Union[int, str]] = None
    reply_count: Optional[int] = None
    published: Optional[str] = None
    is_author: bool = False
    is_pinned: bool = False
    is_hearted: bool = False
    author_avatar: Optional[str] = None
    author_url: Optional[str] = None
    reply_continuation: Optional[str] = None

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            return getattr(self, item)
        raise KeyError(item)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "author": self.author,
            "author_id": self.author_id,
            "like_count": self.like_count,
            "reply_count": self.reply_count,
            "published": self.published,
            "is_author": self.is_author,
            "is_pinned": self.is_pinned,
            "is_hearted": self.is_hearted,
            "author_avatar": self.author_avatar,
            "author_url": self.author_url,
            "reply_continuation": self.reply_continuation,
        }


class Reply(Comment):
    pass


@dataclass
class CommentPage:
    comments: List[Comment]
    continuation: Optional[str]
    has_more: bool

    def __getitem__(self, item: str) -> Any:
        if item == "comments":
            return self.comments
        elif item == "continuation":
            return self.continuation
        elif item == "has_more":
            return self.has_more
        raise KeyError(item)

    def get(self, key: str, default: Any = None) -> Any:
        if key == "comments":
            return self.comments
        elif key == "continuation":
            return self.continuation
        elif key == "has_more":
            return self.has_more
        return default


def _get_runs_text(source: Any) -> str:
    if not source or not isinstance(source, dict):
        return ""
    if "simpleText" in source and isinstance(source["simpleText"], str):
        return source["simpleText"]
    runs = source.get("runs")
    if isinstance(runs, list):
        return "".join(
            run.get("text", "") for run in runs if isinstance(run, dict) and "text" in run
        )
    return ""


def _parse_mutations(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    muts: Dict[str, Dict[str, Any]] = {}
    mutations = get_value(
        data, ["frameworkUpdates", "entityBatchUpdate", "mutations"]
    )
    if isinstance(mutations, list):
        for m in mutations:
            if not isinstance(m, dict):
                continue
            payload = m.get("payload", {})
            if isinstance(payload, dict) and "commentEntityPayload" in payload:
                cp = payload["commentEntityPayload"]
                if isinstance(cp, dict):
                    key = cp.get("key")
                    if key and isinstance(key, str):
                        muts[key] = cp
    return muts


def _extract_continuation_token(item: Dict[str, Any]) -> Optional[str]:
    if not isinstance(item, dict):
        return None
    cir = item.get("continuationItemRenderer")
    if not isinstance(cir, dict):
        return None

    token = get_value(
        cir, ["continuationEndpoint", "continuationCommand", "token"]
    ) or get_value(
        cir,
        [
            "button",
            "buttonRenderer",
            "command",
            "continuationCommand",
            "token",
        ],
    ) or get_value(
        cir, ["continuationEndpoint", "token"]
    ) or get_value(
        cir, ["continuationCommand", "token"]
    )
    if token and isinstance(token, str):
        return token
    return None


def _parse_comment_from_view_model(
    cvm: Dict[str, Any], mutations: Dict[str, Dict[str, Any]]
) -> Optional[Comment]:
    if not isinstance(cvm, dict):
        return None
    vm = cvm.get("commentViewModel") if "commentViewModel" in cvm else cvm
    if not isinstance(vm, dict):
        return None

    comment_key = vm.get("commentKey")
    comment_id = vm.get("commentId")
    pinned_text = vm.get("pinnedText")

    payload = mutations.get(comment_key) if comment_key else None
    if not payload or not isinstance(payload, dict):
        if comment_id:
            return Comment(
                id=str(comment_id),
                text="",
                author="",
                is_pinned=bool(pinned_text),
            )
        return None

    properties = payload.get("properties", {}) or {}
    author_info = payload.get("author", {}) or {}
    toolbar_info = payload.get("toolbar", {}) or {}

    cid = properties.get("commentId") or comment_id or ""
    content_dict = properties.get("content", {}) or {}
    text = content_dict.get("content", "") if isinstance(content_dict, dict) else ""
    published = properties.get("publishedTime")

    author_name = author_info.get("displayName") or ""
    author_id = author_info.get("channelId")
    author_avatar = author_info.get("avatarThumbnailUrl")

    channel_cmd = get_value(
        author_info, ["channelCommand", "innertubeCommand", "browseEndpoint"]
    )
    author_url = None
    if isinstance(channel_cmd, dict) and channel_cmd.get("canonicalBaseUrl"):
        author_url = f"https://www.youtube.com{channel_cmd['canonicalBaseUrl']}"
    elif author_id:
        author_url = build_channel_url(author_id)

    is_author = bool(
        author_info.get("isCreator")
        or author_info.get("isCurrentUser")
        or properties.get("authorIsChannelOwner")
    )
    is_pinned = bool(pinned_text or properties.get("pinnedText"))
    is_hearted = bool(
        toolbar_info.get("heartActiveTooltip")
        or toolbar_info.get("creatorThumbnailUrl")
    )

    like_count = toolbar_info.get("likeCountNotliked") or toolbar_info.get(
        "likeCountLiked"
    )

    reply_count_raw = toolbar_info.get("replyCount")
    reply_count: Optional[int] = None
    if reply_count_raw is not None:
        try:
            reply_count = int(str(reply_count_raw).replace(",", "").strip())
        except ValueError:
            reply_count = None

    return Comment(
        id=str(cid),
        text=str(text),
        author=str(author_name),
        author_id=author_id,
        like_count=like_count,
        reply_count=reply_count,
        published=published,
        is_author=is_author,
        is_pinned=is_pinned,
        is_hearted=is_hearted,
        author_avatar=author_avatar,
        author_url=author_url,
    )


def _parse_comment_from_renderer(renderer: Dict[str, Any]) -> Optional[Comment]:
    if not isinstance(renderer, dict):
        return None

    cid = renderer.get("commentId")
    if not cid:
        return None

    text = _get_runs_text(renderer.get("contentText"))
    author = _get_runs_text(renderer.get("authorText")) or renderer.get(
        "authorText", {}
    ).get("simpleText", "")
    author_id = get_value(
        renderer, ["authorEndpoint", "browseEndpoint", "browseId"]
    )
    author_avatar = get_value(renderer, ["authorThumbnail", "thumbnails", 0, "url"])
    author_url = build_channel_url(author_id) if author_id else None

    published = _get_runs_text(renderer.get("publishedTimeText"))
    is_author = bool(renderer.get("authorIsChannelOwner", False))
    is_pinned = bool(renderer.get("pinnedCommentBadge"))

    action_buttons = renderer.get("actionButtons", {})
    is_hearted = bool(
        get_value(
            action_buttons, ["commentActionButtonsRenderer", "creatorHeart"]
        )
    )

    vote_count = renderer.get("voteCount")
    like_count = _get_runs_text(vote_count) if isinstance(vote_count, dict) else None

    reply_count_raw = renderer.get("replyCount")
    reply_count: Optional[int] = None
    if reply_count_raw is not None:
        try:
            reply_count = int(reply_count_raw)
        except (ValueError, TypeError):
            reply_count = None

    return Comment(
        id=str(cid),
        text=text,
        author=author,
        author_id=author_id,
        like_count=like_count,
        reply_count=reply_count,
        published=published,
        is_author=is_author,
        is_pinned=is_pinned,
        is_hearted=is_hearted,
        author_avatar=author_avatar,
        author_url=author_url,
    )


def _parse_comment_thread(
    thread: Dict[str, Any], mutations: Dict[str, Dict[str, Any]]
) -> Tuple[Optional[Comment], List[Comment], Optional[str]]:
    if not isinstance(thread, dict):
        return None, [], None

    comment: Optional[Comment] = None
    if "commentViewModel" in thread:
        comment = _parse_comment_from_view_model(
            thread["commentViewModel"], mutations
        )
    elif "comment" in thread and "commentRenderer" in thread["comment"]:
        comment = _parse_comment_from_renderer(thread["comment"]["commentRenderer"])

    inline_replies: List[Comment] = []
    reply_continuation_token: Optional[str] = None

    replies = thread.get("replies")
    if isinstance(replies, dict):
        comment_replies = replies.get("commentRepliesRenderer", {})
        contents = comment_replies.get("contents")
        if isinstance(contents, list):
            for c in contents:
                if not isinstance(c, dict):
                    continue
                if "continuationItemRenderer" in c:
                    reply_continuation_token = _extract_continuation_token(c)
                elif "commentViewModel" in c:
                    rep = _parse_comment_from_view_model(c["commentViewModel"], mutations)
                    if rep:
                        inline_replies.append(rep)
                elif "commentRenderer" in c:
                    rep = _parse_comment_from_renderer(c["commentRenderer"])
                    if rep:
                        inline_replies.append(rep)

    if comment and reply_continuation_token:
        comment.reply_continuation = reply_continuation_token

    return comment, inline_replies, reply_continuation_token


class CommentsCore(RequestCore):
    def __init__(
        self,
        timeout: float = 7.0,
        max_retries: int = 2,
        proxy: Optional[str] = None,
        visitor_data: Optional[str] = None,
        po_token: Optional[str] = None,
        po_token_verifier: Optional[Callable[..., Any]] = None,
    ) -> None:
        super().__init__(
            timeout=timeout,
            max_retries=max_retries,
            proxy=proxy,
            visitor_data=visitor_data,
            po_token=po_token,
            po_token_verifier=po_token_verifier,
        )

    async def fetch_initial_comments_token(self, video_id: str) -> Optional[str]:
        clean_id = get_video_id(video_id)
        self.url = self._build_url("next")
        self.data = self._build_payload(videoId=clean_id)
        resp = await self.post_request()
        if not resp:
            raise RequestError("Failed to fetch video page for comments.")

        data = await resp.json()

        panels = data.get("engagementPanels", [])
        if isinstance(panels, list):
            for panel in panels:
                if not isinstance(panel, dict):
                    continue
                p_id = get_value(
                    panel,
                    ["engagementPanelSectionListRenderer", "panelIdentifier"],
                ) or get_value(
                    panel,
                    ["engagementPanelSectionListRenderer", "targetId"],
                )
                if p_id == "engagement-panel-comments-section" or (
                    isinstance(p_id, str) and "comment" in p_id
                ):
                    content = get_value(
                        panel,
                        ["engagementPanelSectionListRenderer", "content"],
                    )
                    if isinstance(content, dict):
                        section_list = content.get("sectionListRenderer", {})
                        contents = section_list.get("contents", [])
                        if isinstance(contents, list):
                            for item in contents:
                                if not isinstance(item, dict):
                                    continue
                                sub_contents = get_value(
                                    item, ["itemSectionRenderer", "contents"]
                                )
                                if isinstance(sub_contents, list):
                                    for sub in sub_contents:
                                        tok = _extract_continuation_token(sub)
                                        if tok:
                                            return tok

        # Fallback recursive search for comment-item-section
        def find_comment_section_token(obj: Any) -> Optional[str]:
            if isinstance(obj, dict):
                if obj.get("sectionIdentifier") == "comment-item-section":
                    contents = obj.get("contents", [])
                    if isinstance(contents, list):
                        for c in contents:
                            tok = _extract_continuation_token(c)
                            if tok:
                                return tok
                for v in obj.values():
                    res = find_comment_section_token(v)
                    if res:
                        return res
            elif isinstance(obj, list):
                for item in obj:
                    res = find_comment_section_token(item)
                    if res:
                        return res
            return None

        return find_comment_section_token(data)

    async def fetch_comments_page(
        self, continuation_token: str
    ) -> Tuple[List[Comment], Optional[str], Dict[str, str]]:
        self.url = self._build_url("next")
        self.data = self._build_payload(continuation=continuation_token)
        resp = await self.post_request()
        if not resp:
            return [], None, {}

        data = await resp.json()
        mutations = _parse_mutations(data)

        endpoints = data.get("onResponseReceivedEndpoints", []) or data.get(
            "onResponseReceivedCommands", []
        )
        if not isinstance(endpoints, list):
            return [], None, {}

        comments: List[Comment] = []
        next_continuation_token: Optional[str] = None
        reply_tokens: Dict[str, str] = {}

        for ep in endpoints:
            if not isinstance(ep, dict):
                continue
            cmd = ep.get("reloadContinuationItemsCommand") or ep.get(
                "appendContinuationItemsAction"
            )
            if not isinstance(cmd, dict):
                continue

            items = cmd.get("continuationItems", [])
            if not isinstance(items, list):
                continue

            for item in items:
                if not isinstance(item, dict):
                    continue

                if "commentThreadRenderer" in item:
                    thread = item["commentThreadRenderer"]
                    c, _inline_reps, rep_tok = _parse_comment_thread(
                        thread, mutations
                    )
                    if c:
                        comments.append(c)
                        if rep_tok:
                            reply_tokens[c.id] = rep_tok
                elif "commentViewModel" in item:
                    c = _parse_comment_from_view_model(item["commentViewModel"], mutations)
                    if c:
                        comments.append(c)
                elif "commentRenderer" in item:
                    c = _parse_comment_from_renderer(item["commentRenderer"])
                    if c:
                        comments.append(c)

                if "continuationItemRenderer" in item:
                    tok = _extract_continuation_token(item)
                    if tok:
                        next_continuation_token = tok

        return comments, next_continuation_token, reply_tokens

    async def fetch_replies_page(
        self, continuation_token: str
    ) -> Tuple[List[Comment], Optional[str]]:
        self.url = self._build_url("next")
        self.data = self._build_payload(continuation=continuation_token)
        resp = await self.post_request()
        if not resp:
            return [], None

        data = await resp.json()
        mutations = _parse_mutations(data)

        endpoints = data.get("onResponseReceivedEndpoints", []) or data.get(
            "onResponseReceivedCommands", []
        )
        if not isinstance(endpoints, list):
            return [], None

        replies: List[Comment] = []
        next_continuation_token: Optional[str] = None

        for ep in endpoints:
            if not isinstance(ep, dict):
                continue
            cmd = ep.get("appendContinuationItemsAction") or ep.get(
                "reloadContinuationItemsCommand"
            )
            if not isinstance(cmd, dict):
                continue

            items = cmd.get("continuationItems", [])
            if not isinstance(items, list):
                continue

            for item in items:
                if not isinstance(item, dict):
                    continue

                if "commentViewModel" in item:
                    c = _parse_comment_from_view_model(item["commentViewModel"], mutations)
                    if c:
                        replies.append(c)
                elif "commentRenderer" in item:
                    c = _parse_comment_from_renderer(item["commentRenderer"])
                    if c:
                        replies.append(c)

                if "continuationItemRenderer" in item:
                    tok = _extract_continuation_token(item)
                    if tok:
                        next_continuation_token = tok

        return replies, next_continuation_token


class RepliesPaginator:
    def __init__(
        self,
        comment_id: str,
        continuation: Optional[str] = None,
        inline_replies: Optional[List[Comment]] = None,
        timeout: float = 7.0,
        max_retries: int = 2,
        proxy: Optional[str] = None,
        visitor_data: Optional[str] = None,
        po_token: Optional[str] = None,
        po_token_verifier: Optional[Callable[..., Any]] = None,
    ) -> None:
        self.comment_id: str = comment_id
        self.continuation: Optional[str] = continuation
        self.has_more: bool = continuation is not None or bool(inline_replies)
        self._inline_replies: List[Comment] = inline_replies or []
        self._fetched_initial: bool = False
        self._core: CommentsCore = CommentsCore(
            timeout=timeout,
            max_retries=max_retries,
            proxy=proxy,
            visitor_data=visitor_data,
            po_token=po_token,
            po_token_verifier=po_token_verifier,
        )

    async def get(self) -> CommentPage:
        if self._fetched_initial:
            return CommentPage(
                comments=[], continuation=self.continuation, has_more=self.has_more
            )

        self._fetched_initial = True

        if self.continuation:
            replies, next_tok = await self._core.fetch_replies_page(self.continuation)
            combined = self._inline_replies + replies
            self.continuation = next_tok
            self.has_more = next_tok is not None
            return CommentPage(
                comments=combined,
                continuation=self.continuation,
                has_more=self.has_more,
            )
        elif self._inline_replies:
            res = self._inline_replies
            self._inline_replies = []
            self.has_more = False
            return CommentPage(comments=res, continuation=None, has_more=False)
        else:
            self.has_more = False
            return CommentPage(comments=[], continuation=None, has_more=False)

    async def next(self) -> CommentPage:
        if not self._fetched_initial:
            return await self.get()

        if not self.has_more or not self.continuation:
            self.has_more = False
            self.continuation = None
            return CommentPage(comments=[], continuation=None, has_more=False)

        replies, next_tok = await self._core.fetch_replies_page(self.continuation)
        self.continuation = next_tok
        self.has_more = next_tok is not None
        return CommentPage(
            comments=replies, continuation=self.continuation, has_more=self.has_more
        )

    def __aiter__(self) -> Any:
        async def _generator() -> Any:
            page = await self.get()
            for reply in page.comments:
                yield reply
            while page.has_more:
                page = await self.next()
                for reply in page.comments:
                    yield reply

        return _generator()

    def __await__(self) -> Any:
        async def _wrap() -> "RepliesPaginator":
            return self

        return _wrap().__await__()


class CommentsPaginator:
    def __init__(
        self,
        video_link_or_id: str,
        timeout: float = 7.0,
        max_retries: int = 2,
        proxy: Optional[str] = None,
        visitor_data: Optional[str] = None,
        po_token: Optional[str] = None,
        po_token_verifier: Optional[Callable[..., Any]] = None,
    ) -> None:
        self.video_id: str = get_video_id(video_link_or_id)
        self.continuation: Optional[str] = None
        self.has_more: bool = True
        self._fetched_initial: bool = False
        self._reply_tokens: Dict[str, str] = {}
        self._comments_cache: Dict[str, Comment] = {}

        self._timeout: float = timeout
        self._max_retries: int = max_retries
        self._proxy: Optional[str] = proxy
        self._visitor_data: Optional[str] = visitor_data
        self._po_token: Optional[str] = po_token
        self._po_token_verifier: Optional[Callable[..., Any]] = po_token_verifier

        self._core: CommentsCore = CommentsCore(
            timeout=timeout,
            max_retries=max_retries,
            proxy=proxy,
            visitor_data=visitor_data,
            po_token=po_token,
            po_token_verifier=po_token_verifier,
        )

    async def _init_comments(self) -> None:
        if self._fetched_initial:
            return
        self._fetched_initial = True
        token = await self._core.fetch_initial_comments_token(self.video_id)
        if token:
            self.continuation = token
            self.has_more = True
        else:
            self.continuation = None
            self.has_more = False

    async def get(self) -> CommentPage:
        if not self._fetched_initial:
            await self._init_comments()
            if not self.continuation:
                return CommentPage(comments=[], continuation=None, has_more=False)

        if not self.continuation:
            self.has_more = False
            return CommentPage(comments=[], continuation=None, has_more=False)

        comments, next_tok, reply_toks = await self._core.fetch_comments_page(
            self.continuation
        )
        self.continuation = next_tok
        self.has_more = next_tok is not None
        self._reply_tokens.update(reply_toks)
        for c in comments:
            self._comments_cache[c.id] = c

        return CommentPage(
            comments=comments, continuation=self.continuation, has_more=self.has_more
        )

    async def next(self) -> CommentPage:
        if not self._fetched_initial:
            return await self.get()

        if not self.has_more or not self.continuation:
            self.has_more = False
            self.continuation = None
            return CommentPage(comments=[], continuation=None, has_more=False)

        comments, next_tok, reply_toks = await self._core.fetch_comments_page(
            self.continuation
        )
        self.continuation = next_tok
        self.has_more = next_tok is not None
        self._reply_tokens.update(reply_toks)
        for c in comments:
            self._comments_cache[c.id] = c

        return CommentPage(
            comments=comments, continuation=self.continuation, has_more=self.has_more
        )

    def replies(self, comment_id: str) -> RepliesPaginator:
        token = self._reply_tokens.get(comment_id)
        if not token:
            comment = self._comments_cache.get(comment_id)
            if comment and comment.reply_continuation:
                token = comment.reply_continuation

        return RepliesPaginator(
            comment_id=comment_id,
            continuation=token,
            timeout=self._timeout,
            max_retries=self._max_retries,
            proxy=self._proxy,
            visitor_data=self._visitor_data,
            po_token=self._po_token,
            po_token_verifier=self._po_token_verifier,
        )

    def __aiter__(self) -> Any:
        async def _generator() -> Any:
            page = await self.get()
            for comment in page.comments:
                yield comment
            while page.has_more:
                page = await self.next()
                for comment in page.comments:
                    yield comment

        return _generator()

    def __await__(self) -> Any:
        async def _wrap() -> "CommentsPaginator":
            return self

        return _wrap().__await__()
