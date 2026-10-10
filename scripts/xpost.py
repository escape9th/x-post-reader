#!/usr/bin/env python3
"""xpost — read and browse X/Twitter without login or an API key.

Powered by the free public mirror API (FxEmbed / fxtwitter) and Twitter's
official syndication endpoint. Standard library only — no pip install.

Usage:
  xpost.py tweet <url-or-id>                 one post, full detail (incl. X Article)
  xpost.py thread <url-or-id>                unroll a thread
  xpost.py replies <url-or-id>               thread + comments (the reply section)
  xpost.py timeline <handle> [--count N] [--replies]
  xpost.py media <handle>                    posts with media
  xpost.py followers <handle>                list of followers
  xpost.py following <handle>                list of accounts they follow
  xpost.py user <handle>                     profile
  xpost.py trending [--count N]              trending topics
  xpost.py search <query> [--count N]        search posts (may return empty)
  xpost.py search-users <query>              search people
  xpost.py batch <file>                      read many posts (one URL/id per line)

Environment:
  HTTP_PROXY / HTTPS_PROXY   honoured automatically (also Windows system proxy).
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

UA = "curl/8.0"
V1 = "https://api.fxtwitter.com"
V2 = "https://api.fxtwitter.com/2"
SYND = "https://cdn.syndication.twimg.com/tweet-result"

TWEET_URL_RE = re.compile(
    r"(?:https?://)?(?:www\.|mobile\.)?(?:x|twitter)\.com/"
    r"([A-Za-z0-9_]{1,20})/status/(\d{10,25})", re.I)
BARE_ID_RE = re.compile(r"^\d{10,25}$")


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def get_json(url, timeout=30):
    return json.loads(get(url, timeout).decode("utf-8"))


def parse_ref(value):
    m = TWEET_URL_RE.search(value.strip())
    if m:
        return m.group(1), m.group(2)
    if BARE_ID_RE.match(value.strip()):
        return None, value.strip()
    return None, None


# ---------------- v1: single post with full detail --------------------------

def v1_tweet(ref):
    handle, tid = parse_ref(ref)
    if not tid:
        raise SystemExit(f"error: could not parse a tweet id from: {ref!r}")
    errors = []
    for name, url in (
        ("fxtwitter", f"{V1}/i/status/{tid}" if not handle else f"{V1}/{handle}/status/{tid}"),
        ("vxtwitter", f"https://api.vxtwitter.com/{handle}/status/{tid}" if handle else f"https://api.vxtwitter.com/i/status/{tid}"),
        ("syndication", f"{SYND}?id={tid}&lang=en&token=a"),
    ):
        try:
            d = get_json(url)
            if name == "syndication":
                if d.get("__typename") == "Tweet":
                    return name, _normalise_syndication(d)
            else:
                if d.get("tweet"):
                    return name, d["tweet"]
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError) as e:
            errors.append(f"{name}: {e}")
    raise SystemExit("error: all tweet sources failed.\n  " + "\n  ".join(errors))


def _normalise_syndication(d):
    u = d.get("user") or {}
    return {
        "url": f"https://x.com/{u.get('screen_name')}/status/{d.get('id_str')}",
        "id": d.get("id_str"),
        "text": d.get("full_text") or d.get("text") or "",
        "created_at": d.get("created_at"),
        "likes": d.get("favorite_count"),
        "retweets": d.get("retweet_count"),
        "replies": d.get("conversation_count"),
        "author": {"name": u.get("name"), "screen_name": u.get("screen_name"),
                   "followers": u.get("followers_count")},
        "media": d.get("media"),
    }


def _article_text(article):
    if not article:
        return ""
    blocks = (article.get("content") or {}).get("blocks") or []
    parts = [f"### {article.get('title', '')}"]
    for b in blocks:
        parts.append(b.get("text") or "")
    return "\n\n".join(parts)


def fmt_v1(source, t):
    a = t.get("author") or {}
    lines = [
        f"### {a.get('name')} (@{a.get('screen_name')})",
        f"URL: {t.get('url')}  (source: {source})",
    ]
    if t.get("created_at"):
        lines.append(f"created: {t.get('created_at')}")
    lines.append(
        f"likes={t.get('likes')} reposts={t.get('retweets')} replies={t.get('replies')} "
        f"quotes={t.get('quotes')} bookmarks={t.get('bookmarks')} views={t.get('views')}")
    lines += ["", (t.get('text') or '').strip()]
    art = _article_text(t.get("article"))
    if art:
        lines += ["", "--- long-form post (X Article) ---", art]
    if t.get("quote"):
        q = t["quote"]
        qa = q.get("author") or {}
        lines += ["", f"> quoted @{qa.get('screen_name')}: {q.get('text')}"]
    media = t.get("media") or {}
    for key in ("videos", "photos"):
        for item in (media.get(key) or []):
            lines.append(f"media[{key}]: {item.get('url')}")
    return "\n".join(lines)


# ---------------- v2: browse endpoints --------------------------------------

def _status_line(s, full=False):
    a = s.get("author") or {}
    txt = (s.get("text") or "").strip().replace("\n", " ")
    head = f"@{a.get('screen_name', '?')}"
    meta = []
    for k in ("likes", "reposts", "replies", "bookmarks"):
        if s.get(k) is not None:
            meta.append(f"{k}={s[k]}")
    if s.get("created_at"):
        meta.append(str(s["created_at"])[:16])
    line = f"{head} ({s.get('id')})"
    if meta:
        line += "  [" + ", ".join(meta) + "]"
    line += f"\n    {txt if full else txt[:200]}"
    return line


def _cursor_hint(d):
    c = d.get("cursor") or {}
    if c.get("bottom"):
        return f"(more available: --cursor {c['bottom']})"
    return ""


def cmd_tweet(args):
    source, t = v1_tweet(args.ref)
    if args.json:
        print(json.dumps(t, ensure_ascii=False, indent=2))
    else:
        print(fmt_v1(source, t))


def cmd_thread(args):
    handle, tid = parse_ref(args.ref)
    if not tid:
        raise SystemExit(f"error: bad ref {args.ref!r}")
    d = get_json(f"{V2}/thread/{tid}")
    thread = d.get("thread") or []
    print(f"thread: {len(thread)} posts")
    for s in thread:
        print(_status_line(s, full=True))
        print()


def cmd_replies(args):
    handle, tid = parse_ref(args.ref)
    if not tid:
        raise SystemExit(f"error: bad ref {args.ref!r}")
    d = get_json(f"{V2}/conversation/{tid}")
    root = d.get("status")
    thread = d.get("thread") or []
    replies = d.get("replies") or []
    print(f"### ROOT POST: {_status_line(root, full=True)}\n")
    if thread:
        print(f"--- thread ({len(thread)}) ---")
        for s in thread:
            print(_status_line(s, full=True))
        print()
    print(f"--- replies ({len(replies)}) ---")
    for s in replies[: args.count]:
        print(_status_line(s, full=True))
        print()
    print(_cursor_hint(d))


def cmd_timeline(args):
    h = args.handle.lstrip("@")
    q = urllib.parse.urlencode({
        "count": args.count,
        "with_replies": "1" if args.replies else "0",
    })
    d = get_json(f"{V2}/profile/{h}/statuses?{q}")
    res = d.get("results") or []
    print(f"@{h}: {len(res)} posts")
    for s in res:
        print(_status_line(s))
    print(_cursor_hint(d))


def cmd_media(args):
    h = args.handle.lstrip("@")
    d = get_json(f"{V2}/profile/{h}/media?count={args.count}")
    for s in (d.get("results") or []):
        print(_status_line(s))
    print(_cursor_hint(d))


def _people_list(args, which):
    h = args.handle.lstrip("@")
    d = get_json(f"{V2}/profile/{h}/{which}?count={args.count}")
    res = d.get("results") or []
    print(f"@{h} {which}: {len(res)}")
    for it in res:
        u = it.get("user") or it
        print(f"  @{u.get('screen_name')}  {u.get('name')}  followers={u.get('followers')} following={u.get('following')}")
    print(_cursor_hint(d))


def cmd_followers(args):
    _people_list(args, "followers")


def cmd_following(args):
    _people_list(args, "following")


def cmd_user(args):
    h = args.handle.lstrip("@")
    d = get_json(f"{V2}/profile/{h}")
    print(json.dumps(d.get("user") or d, ensure_ascii=False, indent=2))


def cmd_trending(args):
    d = get_json(f"{V2}/trends?count={args.count}")
    for t in (d.get("trends") or []):
        print(f"- {t.get('name')}  ({t.get('context', '')})")


def cmd_search(args):
    q = urllib.parse.urlencode({"q": args.query, "count": args.count, "feed": args.feed})
    try:
        d = get_json(f"{V2}/search?{q}")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("no results (free search may not index this query)")
            return
        raise
    res = d.get("results") or []
    print(f"search '{args.query}': {len(res)} results")
    for it in res:
        s = it.get("status") or it
        print(_status_line(s))
    print(_cursor_hint(d))


def cmd_search_users(args):
    q = urllib.parse.urlencode({"q": args.query, "count": args.count})
    d = get_json(f"{V2}/search/users?{q}")
    for it in (d.get("results") or []):
        u = it.get("user") or it
        print(f"  @{u.get('screen_name')}  {u.get('name')}  followers={u.get('followers')}")
    print(_cursor_hint(d))


def cmd_batch(args):
    refs = [ln.strip() for ln in open(args.file, encoding="utf-8") if ln.strip()]
    for ref in refs:
        try:
            source, t = v1_tweet(ref)
            print(fmt_v1(source, t))
        except SystemExit as e:
            print(f"[{ref}] -> {e}")
        print("\n" + "-" * 72 + "\n")


def main(argv=None):
    p = argparse.ArgumentParser(prog="xpost", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("tweet", help="one post, full detail")
    t.add_argument("ref")
    t.add_argument("--json", action="store_true")
    t.set_defaults(fn=cmd_tweet)

    th = sub.add_parser("thread", help="unroll a thread")
    th.add_argument("ref")
    th.set_defaults(fn=cmd_thread)

    r = sub.add_parser("replies", help="thread + comments")
    r.add_argument("ref")
    r.add_argument("--count", type=int, default=20)
    r.set_defaults(fn=cmd_replies)

    tl = sub.add_parser("timeline", help="a user's recent posts")
    tl.add_argument("handle")
    tl.add_argument("--count", type=int, default=20)
    tl.add_argument("--replies", action="store_true")
    tl.set_defaults(fn=cmd_timeline)

    m = sub.add_parser("media", help="a user's posts with media")
    m.add_argument("handle")
    m.add_argument("--count", type=int, default=20)
    m.set_defaults(fn=cmd_media)

    f = sub.add_parser("followers", help="list followers")
    f.add_argument("handle")
    f.add_argument("--count", type=int, default=50)
    f.set_defaults(fn=cmd_followers)

    fg = sub.add_parser("following", help="list accounts they follow")
    fg.add_argument("handle")
    fg.add_argument("--count", type=int, default=50)
    fg.set_defaults(fn=cmd_following)

    u = sub.add_parser("user", help="profile")
    u.add_argument("handle")
    u.set_defaults(fn=cmd_user)

    tr = sub.add_parser("trending", help="trending topics")
    tr.add_argument("--count", type=int, default=20)
    tr.set_defaults(fn=cmd_trending)

    s = sub.add_parser("search", help="search posts (may be empty)")
    s.add_argument("query")
    s.add_argument("--count", type=int, default=20)
    s.add_argument("--feed", default="latest", choices=["latest", "top"])
    s.set_defaults(fn=cmd_search)

    su = sub.add_parser("search-users", help="search people")
    su.add_argument("query")
    su.add_argument("--count", type=int, default=20)
    su.set_defaults(fn=cmd_search_users)

    b = sub.add_parser("batch", help="read many posts")
    b.add_argument("file")
    b.set_defaults(fn=cmd_batch)

    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
