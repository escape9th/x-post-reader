"""xpost MCP server — browse X/Twitter from any MCP client.

Exposes the same capabilities as scripts/xpost.py as MCP tools, so Claude
Desktop / Codex / Cursor / any MCP host can call them directly instead of
running a script.

Install:
    pip install mcp        # or: uv pip install mcp
Run (stdio transport):
    python mcp/server.py
"""
import json
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import xpost  # noqa: E402  (reuse the CLI's API layer)

from mcp.server.fastmcp import FastMCP  # noqa: E402

mcp = FastMCP("xpost")


def _err(e):
    raise RuntimeError(str(e))


def _compact(t):
    """Trim a tweet/status object to the fields an LLM actually needs."""
    a = t.get("author") or {}
    out = {
        "id": t.get("id"),
        "url": t.get("url"),
        "text": t.get("text"),
        "author": {
            "name": a.get("name"),
            "screen_name": a.get("screen_name"),
            "followers": a.get("followers"),
        },
        "created_at": t.get("created_at"),
        "likes": t.get("likes"),
        "reposts": t.get("reposts") if t.get("reposts") is not None else t.get("retweets"),
        "replies": t.get("replies"),
        "bookmarks": t.get("bookmarks"),
        "views": t.get("views"),
    }
    art = t.get("article")
    if art:
        blocks = (art.get("content") or {}).get("blocks") or []
        out["article"] = {
            "title": art.get("title"),
            "text": "\n".join((b.get("text") or "") for b in blocks),
        }
    media = t.get("media") or {}
    urls = []
    for key in ("videos", "photos"):
        for it in (media.get(key) or []):
            if it.get("url"):
                urls.append(it["url"])
    if urls:
        out["media"] = urls
    return out


def _dump(obj):
    return json.dumps(obj, ensure_ascii=False)


@mcp.tool()
def get_tweet(url_or_id: str) -> str:
    """Read one X/Twitter post: full text, author, engagement, media, and the full
    long-form (X Article) body if present. Pass an x.com/twitter.com URL or a bare
    numeric id. Read-only."""
    try:
        _src, t = xpost.v1_tweet(url_or_id)
    except SystemExit as e:
        _err(e)
    return _dump(_compact(t))


@mcp.tool()
def get_replies(url_or_id: str, count: int = 20) -> str:
    """Get the comments/replies under a post, plus its thread. count caps how many
    replies are returned (default 20). Read-only."""
    _h, tid = xpost.parse_ref(url_or_id)
    if not tid:
        _err(f"could not parse a tweet id from {url_or_id!r}")
    d = xpost.get_json(f"{xpost.V2}/conversation/{tid}")
    out = {
        "root": _compact(d.get("status")),
        "thread": [_compact(s) for s in (d.get("thread") or [])],
        "replies": [_compact(s) for s in (d.get("replies") or [])[:count]],
        "cursor": d.get("cursor"),
    }
    return _dump(out)


@mcp.tool()
def get_thread(url_or_id: str) -> str:
    """Unroll a thread (a post and its author's replies to it). Read-only."""
    _h, tid = xpost.parse_ref(url_or_id)
    if not tid:
        _err(f"could not parse a tweet id from {url_or_id!r}")
    d = xpost.get_json(f"{xpost.V2}/thread/{tid}")
    return _dump([_compact(s) for s in (d.get("thread") or [])])


@mcp.tool()
def get_timeline(handle: str, count: int = 20, include_replies: bool = False) -> str:
    """List a user's recent posts (their timeline). Read-only."""
    h = handle.lstrip("@")
    q = urllib.parse.urlencode({"count": count, "with_replies": "1" if include_replies else "0"})
    d = xpost.get_json(f"{xpost.V2}/profile/{h}/statuses?{q}")
    return _dump({"posts": [_compact(s) for s in (d.get("results") or [])], "cursor": d.get("cursor")})


@mcp.tool()
def get_media(handle: str, count: int = 20) -> str:
    """List a user's posts that contain media. Read-only."""
    d = xpost.get_json(f"{xpost.V2}/profile/{handle.lstrip('@')}/media?count={count}")
    return _dump([_compact(s) for s in (d.get("results") or [])])


@mcp.tool()
def get_followers(handle: str, count: int = 50) -> str:
    """List a user's followers. Read-only."""
    d = xpost.get_json(f"{xpost.V2}/profile/{handle.lstrip('@')}/followers?count={count}")
    return _dump({"followers": [it.get("user") for it in (d.get("results") or [])], "cursor": d.get("cursor")})


@mcp.tool()
def get_following(handle: str, count: int = 50) -> str:
    """List the accounts a user follows. Read-only."""
    d = xpost.get_json(f"{xpost.V2}/profile/{handle.lstrip('@')}/following?count={count}")
    return _dump({"following": [it.get("user") for it in (d.get("results") or [])], "cursor": d.get("cursor")})


@mcp.tool()
def get_user(handle: str) -> str:
    """Get a user's profile (bio, followers, join date, counts). Read-only."""
    d = xpost.get_json(f"{xpost.V2}/profile/{handle.lstrip('@')}")
    return _dump(d.get("user") or d)


@mcp.tool()
def get_trending(count: int = 20) -> str:
    """Get currently trending topics on X/Twitter. Read-only."""
    d = xpost.get_json(f"{xpost.V2}/trends?count={count}")
    return _dump(d.get("trends") or [])


@mcp.tool()
def search(query: str, count: int = 20, feed: str = "latest") -> str:
    """Search X/Twitter posts. NOTE: the free index is shallow and often returns
    empty; treat empty results as 'not indexed', not 'nothing exists'. Read-only."""
    q = urllib.parse.urlencode({"q": query, "count": count, "feed": feed})
    try:
        d = xpost.get_json(f"{xpost.V2}/search?{q}")
    except Exception:
        return _dump({"results": [], "note": "search returned no results / not indexed"})
    return _dump({"results": [_compact(it.get("status") or it) for it in (d.get("results") or [])],
                  "cursor": d.get("cursor")})


@mcp.tool()
def search_users(query: str, count: int = 20) -> str:
    """Search X/Twitter users by name or handle. Read-only."""
    q = urllib.parse.urlencode({"q": query, "count": count})
    d = xpost.get_json(f"{xpost.V2}/search/users?{q}")
    return _dump({"users": [it.get("user") for it in (d.get("results") or [])], "cursor": d.get("cursor")})


if __name__ == "__main__":
    mcp.run()
